import math
import os
import sys
import time
import shutil
import numpy as np

# Windows ANSI escape code activation
if os.name == 'nt':
    os.system('')

def mix(c1, c2, t):
    """Linear interpolation between two colors/values."""
    t_c = np.clip(t, 0.0, 1.0)
    if isinstance(c1, (tuple, list)):
        c1 = np.array(c1, dtype=np.float32)
    if isinstance(c2, (tuple, list)):
        c2 = np.array(c2, dtype=np.float32)
    return c1 * (1.0 - t_c) + c2 * t_c

def rot_y(points, angle):
    """Rotate points around Y axis."""
    c, s = math.cos(angle), math.sin(angle)
    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]
    xr = x * c + z * s
    zr = -x * s + z * c
    return np.stack([xr, y, zr], axis=-1)

def rot_x(points, angle):
    """Rotate points around X axis."""
    c, s = math.cos(angle), math.sin(angle)
    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]
    yr = y * c - z * s
    zr = y * s + z * c
    return np.stack([x, yr, zr], axis=-1)

class KrathongModel:
    def __init__(self):
        self.points = []
        self.colors = []
        self.materials = [] # 'petal', 'leaf', 'base', 'candle', 'wick'
        self.build_krathong()

    def build_petal(self, a, op, ln, wd, y0, r0, is_leaf=False):
        # Parametric grid
        u_steps = 14
        v_steps = 9
        u = np.linspace(0.02, 1.0, u_steps, dtype=np.float32)
        v_raw = np.linspace(0.0, 1.0, v_steps, dtype=np.float32)
        U, V = np.meshgrid(u, v_raw, indexing='ij')

        v = V * 2.0 - 1.0
        sin_val = np.sin(np.pi * np.clip(U, 0.0, 1.0) ** 0.75)
        w = wd * (np.maximum(0.0, sin_val) ** 0.8) + 0.004
        ly = U * ln
        zl = 0.5 * wd * (1.0 - v * v) * (1.0 - 0.5 * U)
        
        y = ly * math.cos(op) - zl * math.sin(op)
        z = r0 + ly * math.sin(op) + zl * math.cos(op)
        x = v * w

        P = np.stack([x, y, z], axis=-1).reshape(-1, 3)
        U_flat = U.reshape(-1)
        v_flat = v.reshape(-1)

        if is_leaf:
            # Banana leaf base color (shades of rich green with yellow vein accents)
            c1 = np.array([0.15, 0.45, 0.10], dtype=np.float32)
            c2 = np.array([0.55, 0.75, 0.18], dtype=np.float32)
            col = mix(c1, c2, U_flat[:, None])
            # Leaf edge highlight
            edge = 0.25 * (np.abs(v_flat) ** 4)
            col = mix(col, np.array([0.70, 0.85, 0.30], dtype=np.float32), edge[:, None])
            mat = 'leaf'
        else:
            # Lotus petal: pink gradient from soft white-pink tip to vibrant magenta/rose
            c_tip = np.array([1.0, 0.40, 0.72], dtype=np.float32)
            c_base = np.array([1.0, 0.85, 0.92], dtype=np.float32)
            col = mix(c_base, c_tip, (U_flat ** 1.3)[:, None])
            mat = 'petal'

        # Rotate by angle 'a' around Y axis, and shift by y0
        P_rot = rot_y(P, a)
        P_rot[:, 1] += y0

        self.points.append(P_rot)
        self.colors.append(col)
        self.materials.extend([mat] * len(P_rot))

    def build_base(self):
        # Banana trunk disc base
        radii = np.linspace(0.2, 1.25, 8, dtype=np.float32)
        angles = np.linspace(0, 2 * math.pi, 24, endpoint=False, dtype=np.float32)
        r_grid, a_grid = np.meshgrid(radii, angles, indexing='ij')
        
        # Upper and lower layers
        for y_lvl, c_val in [(-0.08, [0.18, 0.38, 0.12]), (-0.22, [0.14, 0.28, 0.08])]:
            x = r_grid * np.cos(a_grid)
            z = r_grid * np.sin(a_grid)
            y = np.full_like(x, y_lvl)
            P = np.stack([x, y, z], axis=-1).reshape(-1, 3)
            col = np.tile(np.array(c_val, dtype=np.float32), (len(P), 1))
            self.points.append(P)
            self.colors.append(col)
            self.materials.extend(['base'] * len(P))

    def build_candle_and_incense(self):
        # Candle cylinder in center
        h_candle = np.linspace(0.0, 0.9, 10, dtype=np.float32)
        a_candle = np.linspace(0, 2 * math.pi, 8, endpoint=False, dtype=np.float32)
        H, A = np.meshgrid(h_candle, a_candle, indexing='ij')
        r_c = 0.09
        x = r_c * np.cos(A)
        z = r_c * np.sin(A)
        y = H
        P = np.stack([x, y, z], axis=-1).reshape(-1, 3)
        col = np.tile(np.array([1.0, 0.95, 0.75], dtype=np.float32), (len(P), 1))
        self.points.append(P)
        self.colors.append(col)
        self.materials.extend(['candle'] * len(P))

        # 3 Incense sticks tilted slightly
        for idx, ang in enumerate([0.5, 2.6, 4.7]):
            h_inc = np.linspace(0.0, 1.4, 14, dtype=np.float32)
            tilt_x = math.cos(ang) * 0.18
            tilt_z = math.sin(ang) * 0.18
            xi = 0.15 * math.cos(ang) + h_inc * (tilt_x / 1.4)
            zi = 0.15 * math.sin(ang) + h_inc * (tilt_z / 1.4)
            yi = h_inc
            P = np.stack([xi, yi, zi], axis=-1)
            # Brown incense stick, glowing tip at top
            col = np.tile(np.array([0.55, 0.25, 0.15], dtype=np.float32), (len(P), 1))
            col[-1] = np.array([1.0, 0.35, 0.1], dtype=np.float32) # burning tip
            self.points.append(P)
            self.colors.append(col)
            self.materials.extend(['incense'] * len(P))

    def build_krathong(self):
        # Layer 1: Outermost green banana leaf folds (ฐานกลีบกระทงใบตอง)
        num_leaves = 14
        for i in range(num_leaves):
            ang = (i / num_leaves) * 2 * math.pi
            self.build_petal(a=ang, op=1.35, ln=1.35, wd=0.45, y0=-0.12, r0=0.85, is_leaf=True)

        # Layer 2: Outer lotus petals (กลีบดอกบัวรอบนอก)
        num_petals_out = 12
        for i in range(num_petals_out):
            ang = ((i + 0.5) / num_petals_out) * 2 * math.pi
            self.build_petal(a=ang, op=1.05, ln=1.20, wd=0.42, y0=-0.05, r0=0.68, is_leaf=False)

        # Layer 3: Middle lotus petals (กลีบดอกบัวรอบกลาง)
        num_petals_mid = 10
        for i in range(num_petals_mid):
            ang = (i / num_petals_mid) * 2 * math.pi
            self.build_petal(a=ang, op=0.70, ln=1.05, wd=0.38, y0=0.02, r0=0.48, is_leaf=False)

        # Layer 4: Inner lotus petals (กลีบดอกบัวรอบใน)
        num_petals_in = 8
        for i in range(num_petals_in):
            ang = ((i + 0.5) / num_petals_in) * 2 * math.pi
            self.build_petal(a=ang, op=0.35, ln=0.90, wd=0.32, y0=0.06, r0=0.28, is_leaf=False)

        # Base and Candle
        self.build_base()
        self.build_candle_and_incense()

        self.static_points = np.concatenate(self.points, axis=0)
        self.static_colors = np.concatenate(self.colors, axis=0)

def main():
    krathong = KrathongModel()
    static_pts = krathong.static_points
    static_cols = krathong.static_colors

    # ASCII character ramps (from subtle dark to intense bright / Matrix-like characters)
    ramp = " `.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8&%WM#@$"
    code_chars = "01*#+~:=·"

    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        t0 = time.time()
        frame_idx = 0

        while True:
            t = time.time() - t0
            term_w, term_h = shutil.get_terminal_size((85, 36))
            W = max(60, min(120, term_w))
            H = max(24, min(45, term_h - 2))

            # Buffers
            z_buffer = np.full((H, W), -1e9, dtype=np.float32)
            char_buffer = np.full((H, W), ' ', dtype=object)
            color_buffer = np.zeros((H, W, 3), dtype=np.float32)

            # 1. Background: Full Moon in the sky
            moon_cx = int(W * 0.78)
            moon_cy = int(H * 0.22)
            moon_r = min(W, H) * 0.16
            
            for y_m in range(max(0, int(moon_cy - moon_r * 1.5)), min(H, int(moon_cy + moon_r * 1.5))):
                for x_m in range(max(0, int(moon_cx - moon_r * 2.8)), min(W, int(moon_cx + moon_r * 2.8))):
                    dx = (x_m - moon_cx) / 2.0  # aspect ratio correction for char width
                    dy = (y_m - moon_cy)
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist <= moon_r:
                        intensity = 1.0 - (dist / moon_r) ** 2 * 0.35
                        z_buffer[y_m, x_m] = -50.0  # distant background
                        c_idx = (x_m + y_m * 3 + frame_idx // 4) % len(code_chars)
                        char_buffer[y_m, x_m] = code_chars[c_idx]
                        # Pale golden moonlight
                        color_buffer[y_m, x_m] = np.array([0.98, 0.95, 0.78]) * intensity
                    elif dist <= moon_r * 1.6:
                        # Soft moon glow
                        glow = (1.0 - (dist - moon_r) / (moon_r * 0.6)) * 0.35
                        if glow > 0.08 and z_buffer[y_m, x_m] < -40.0:
                            char_buffer[y_m, x_m] = '·' if (x_m + y_m) % 2 == 0 else ' '
                            color_buffer[y_m, x_m] = np.array([0.80, 0.75, 0.50]) * glow

            # 2. Distant Floating Lanterns (โคมลอย)
            for i, seed in enumerate([1.2, 3.7, 5.9, 8.4, 11.1]):
                lan_x = int((math.sin(seed + t * 0.08) * 0.35 + 0.35 + (i * 0.15)) * W) % W
                lan_y = int((H * 0.55 - (t * 1.2 + seed * 8.0) % (H * 0.50)))
                if 0 <= lan_x < W and 0 <= lan_y < H:
                    if z_buffer[lan_y, lan_x] < -30.0:
                        char_buffer[lan_y, lan_x] = '▲' if (frame_idx // 6) % 2 == 0 else '*'
                        color_buffer[lan_y, lan_x] = np.array([1.0, 0.65, 0.20])

            # 3. Dynamic Krathong Motion
            # Floating bobbing & tilt on water waves
            bob_y = math.sin(t * 2.2) * 0.06
            tilt_x = math.sin(t * 1.8) * 0.03
            tilt_z = math.cos(t * 1.4) * 0.03
            rot_krathong = t * 0.35  # Gentle slow rotation

            pts = static_pts.copy()
            # Apply tilt and rotation
            pts = rot_x(pts, tilt_x)
            pts = rot_y(pts, rot_krathong)
            pts[:, 1] += bob_y

            # 4. Dynamic Candle Flame & Sparks
            flicker = math.sin(t * 18.0) * 0.04 + math.cos(t * 27.0) * 0.03
            flame_pts = []
            flame_cols = []
            candle_top = 0.95 + bob_y
            
            # Flame core and body
            for f_i in range(24):
                f_phase = (t * 8.0 + f_i * 0.35) % 1.0
                f_y = candle_top + f_phase * 0.45
                f_r = 0.06 * (1.0 - f_phase) + 0.01
                f_ang = f_i * 2.4
                fx = math.cos(f_ang) * f_r + flicker * f_phase
                fz = math.sin(f_ang) * f_r
                flame_pts.append([fx, f_y, fz])
                # Color gradient: bright white/cyan core -> warm golden yellow -> orange/red tip
                if f_phase < 0.25:
                    flame_cols.append([1.0, 1.0, 0.95])
                elif f_phase < 0.65:
                    flame_cols.append([1.0, 0.82, 0.22])
                else:
                    flame_cols.append([1.0, 0.30, 0.05])

            flame_pts = np.array(flame_pts, dtype=np.float32)
            flame_pts = rot_y(flame_pts, rot_krathong)
            flame_cols = np.array(flame_cols, dtype=np.float32)

            all_pts = np.concatenate([pts, flame_pts], axis=0)
            all_cols = np.concatenate([static_cols, flame_cols], axis=0)

            # 5. Camera Transformation
            cam_pitch = 0.42  # Viewing angle looking slightly downward (~24 deg)
            all_pts_cam = rot_x(all_pts, cam_pitch)
            # Offset in camera space: center krathong slightly below middle
            cam_dist = 4.2
            all_pts_cam[:, 2] += cam_dist
            all_pts_cam[:, 1] -= 0.15

            # 3D Projection to Screen
            fov = min(W, H) * 1.6
            aspect = 2.05  # Correct for terminal font height / width ratio
            
            proj_x = (all_pts_cam[:, 0] / all_pts_cam[:, 2]) * fov * aspect + (W * 0.50)
            proj_y = -(all_pts_cam[:, 1] / all_pts_cam[:, 2]) * fov + (H * 0.64)
            depths = -all_pts_cam[:, 2]  # Larger is nearer

            px = proj_x.astype(np.int32)
            py = proj_y.astype(np.int32)

            valid_mask = (px >= 0) & (px < W) & (py >= 0) & (py < H)
            valid_indices = np.where(valid_mask)[0]

            # Render Krathong points
            for idx in valid_indices:
                x_p = px[idx]
                y_p = py[idx]
                dep = depths[idx]

                if dep > z_buffer[y_p, x_p]:
                    z_buffer[y_p, x_p] = dep
                    col = all_cols[idx]
                    color_buffer[y_p, x_p] = col
                    brightness = 0.299 * col[0] + 0.587 * col[1] + 0.114 * col[2]
                    r_idx = int(brightness * (len(code_chars) - 1))
                    r_idx = max(0, min(len(code_chars) - 1, r_idx))
                    char_buffer[y_p, x_p] = code_chars[r_idx]

            # 6. Water Surface & Reflection (ผิวน้ำและแสงสะท้อน)
            water_horizon = int(H * 0.68)
            for yw in range(water_horizon, H):
                water_depth = (yw - water_horizon) / max(1, H - water_horizon)
                for xw in range(W):
                    if z_buffer[yw, xw] < -5.0:  # If no krathong point is directly in front
                        # Water wave ripples
                        wave = math.sin(xw * 0.35 + yw * 0.8 + t * 3.5) * 0.5 + 0.5
                        # Reflection of candle and lotus from upper half
                        mirror_y = max(0, min(H - 1, int(water_horizon - (yw - water_horizon) * 0.75)))
                        refl_col = color_buffer[mirror_y, xw]
                        refl_mag = np.sum(refl_col)

                        if refl_mag > 0.3:
                            # Diffuse watery reflection
                            shimmer = wave * 0.6 + 0.4
                            color_buffer[yw, xw] = refl_col * (0.45 * shimmer)
                            char_buffer[yw, xw] = '~' if wave > 0.5 else '='
                        elif wave > 0.82:
                            # Faint water surface ripple
                            color_buffer[yw, xw] = np.array([0.08, 0.22, 0.35])
                            char_buffer[yw, xw] = '-' if (xw + yw) % 3 == 0 else '.'

            # 7. Build Output Frame String with ANSI TrueColor
            lines = []
            # Title bar header
            status_bar = f"\033[90m[ Loy Krathong ASCII 3D | Frame: {frame_idx:04d} | t={t:5.1f}s | Press Ctrl+C to exit ]\033[0m"
            lines.append(status_bar[:W])

            for y_line in range(H):
                line_parts = []
                cur_r, cur_g, cur_b = -1, -1, -1
                for x_line in range(W):
                    ch = char_buffer[y_line, x_line]
                    if ch == ' ':
                        line_parts.append(' ')
                        cur_r, cur_g, cur_b = -1, -1, -1
                    else:
                        c = color_buffer[y_line, x_line]
                        r_byte = int(np.clip(c[0] * 255, 0, 255))
                        g_byte = int(np.clip(c[1] * 255, 0, 255))
                        b_byte = int(np.clip(c[2] * 255, 0, 255))
                        
                        if (r_byte, g_byte, b_byte) != (cur_r, cur_g, cur_b):
                            cur_r, cur_g, cur_b = r_byte, g_byte, b_byte
                            line_parts.append(f"\033[38;2;{r_byte};{g_byte};{b_byte}m")
                        line_parts.append(ch)
                line_parts.append("\033[0m")
                lines.append("".join(line_parts))

            # Render to terminal without flicker using cursor home
            frame_str = "\033[H" + "\n".join(lines)
            sys.stdout.write(frame_str)
            sys.stdout.flush()

            frame_idx += 1
            # Maintain ~25-30 FPS
            elapsed = time.time() - (t0 + t)
            sleep_time = max(0.005, 0.035 - elapsed)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        pass
    finally:
        # Restore cursor
        sys.stdout.write("\033[?25h\033[0m\n\nEnjoy Loy Krathong Festival!\n")
        sys.stdout.flush()

if __name__ == '__main__':
    main()
