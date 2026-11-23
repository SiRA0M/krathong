import math
import os
import sys
import time
import shutil
import numpy as np

if os.name == 'nt':
    os.system('')

def rot_y(points, angle):
    c, s = math.cos(angle), math.sin(angle)
    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]
    return np.stack([x * c + z * s, y, -x * s + z * c], axis=-1)

def rot_x(points, angle):
    c, s = math.cos(angle), math.sin(angle)
    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]
    return np.stack([x, y * c - z * s, y * s + z * c], axis=-1)

class Compact3DKrathong:
    def __init__(self):
        self.points = []
        self.colors = []
        self.materials = []
        self.build_model()

    def build_petal(self, a, op, ln, wd, y0, r0, mat_type):
        u_steps = 14
        v_steps = 8
        scale = 0.70
        ln *= scale
        wd *= scale
        y0 *= scale
        r0 *= scale

        u = np.linspace(0.02, 1.0, u_steps, dtype=np.float32)
        v_raw = np.linspace(0.0, 1.0, v_steps, dtype=np.float32)
        U, V = np.meshgrid(u, v_raw, indexing='ij')

        v = V * 2.0 - 1.0
        sin_val = np.sin(np.pi * np.clip(U, 0.0, 1.0) ** 0.75)
        w = wd * (np.maximum(0.0, sin_val) ** 0.8) + 0.003
        ly = U * ln
        zl = 0.55 * wd * (1.0 - v * v) * (1.0 - 0.45 * U)

        y = ly * math.cos(op) - zl * math.sin(op)
        z = r0 + ly * math.sin(op) + zl * math.cos(op)
        x = v * w

        P = np.stack([x, y, z], axis=-1).reshape(-1, 3)

        if mat_type == 'leaf':
            col = np.array([140, 225, 35], dtype=np.float32)
        elif mat_type == 'petal_out':
            col = np.array([255, 65, 145], dtype=np.float32)
        elif mat_type == 'petal_mid':
            col = np.array([255, 120, 185], dtype=np.float32)
        elif mat_type == 'petal_in':
            col = np.array([255, 195, 215], dtype=np.float32)
        else:
            col = np.array([255, 195, 45], dtype=np.float32)

        cols = np.tile(col, (len(P), 1))
        P_rot = rot_y(P, a)
        P_rot[:, 1] += y0

        self.points.append(P_rot)
        self.colors.append(cols)
        self.materials.extend([mat_type] * len(P_rot))

    def build_model(self):
        for i in range(16):
            self.build_petal((i / 16.0) * math.pi * 2, 1.38, 1.45, 0.48, -0.15, 0.95, 'leaf')
        for i in range(14):
            self.build_petal(((i + 0.5) / 14.0) * math.pi * 2, 1.10, 1.30, 0.44, -0.08, 0.78, 'petal_out')
        for i in range(12):
            self.build_petal((i / 12.0) * math.pi * 2, 0.78, 1.15, 0.40, -0.02, 0.58, 'petal_mid')
        for i in range(10):
            self.build_petal(((i + 0.5) / 10.0) * math.pi * 2, 0.42, 1.00, 0.35, 0.04, 0.38, 'petal_in')
        for i in range(8):
            self.build_petal((i / 8.0) * math.pi * 2, 0.22, 0.70, 0.28, 0.08, 0.22, 'flower')

        scale = 0.70
        radii = np.linspace(0.20 * scale, 1.35 * scale, 6, dtype=np.float32)
        angles = np.linspace(0, 2 * math.pi, 16, endpoint=False, dtype=np.float32)
        R_grid, A_grid = np.meshgrid(radii, angles, indexing='ij')
        x = (R_grid * np.cos(A_grid)).reshape(-1)
        z = (R_grid * np.sin(A_grid)).reshape(-1)
        y = np.full_like(x, -0.14 * scale)
        P_base = np.stack([x, y, z], axis=-1)
        self.points.append(P_base)
        self.colors.append(np.tile(np.array([45, 110, 30], dtype=np.float32), (len(P_base), 1)))
        self.materials.extend(['base'] * len(P_base))

        h_c = np.linspace(0.05 * scale, 1.0 * scale, 10, dtype=np.float32)
        a_c = np.linspace(0, 2 * math.pi, 8, endpoint=False, dtype=np.float32)
        H_c, A_c = np.meshgrid(h_c, a_c, indexing='ij')
        xc = (0.085 * scale * np.cos(A_c)).reshape(-1)
        zc = (0.085 * scale * np.sin(A_c)).reshape(-1)
        yc = H_c.reshape(-1)
        P_candle = np.stack([xc, yc, zc], axis=-1)
        self.points.append(P_candle)
        self.colors.append(np.tile(np.array([255, 245, 195], dtype=np.float32), (len(P_candle), 1)))
        self.materials.extend(['candle'] * len(P_candle))

        self.static_pts = np.concatenate(self.points, axis=0)
        self.static_cols = np.concatenate(self.colors, axis=0)

def main():
    model = Compact3DKrathong()
    pts_base = model.static_pts
    cols_base = model.static_cols
    mats_base = model.materials

    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    moon_lines = [
        "    #@0000000000@..    ",
        "  +0&@000000000&0000+  ",
        " 00000000000000&000000 ",
        "00000000&0000000000000 ",
        "0000000000000000000000 ",
        " 00000000000000000000  ",
        " &000000000000000000   ",
        "  +0000000000000000    ",
        "   +0000000000000      ",
        "     +000000000        "
    ]

    t0 = time.time()
    frame_idx = 0

    try:
        while True:
            t = time.time() - t0
            term_w, term_h = shutil.get_terminal_size((120, 42))
            W = max(60, min(160, term_w))
            H = max(28, min(65, term_h - 1))

            horizon = int(H * 0.46)
            center_x = int(W * 0.50)

            char_buf = np.full((H, W), ' ', dtype=object)
            col_buf  = np.zeros((H, W, 3), dtype=np.uint8)
            z_buf    = np.full((H, W), -99999.0, dtype=np.float32)

            # 1. Sky & Stars
            np.random.seed(42)
            for _ in range(int(W * 0.7)):
                sc = np.random.randint(0, W)
                sr = np.random.randint(0, horizon)
                shimmer = math.sin(t * 2.0 + sc) * 0.5 + 0.5
                if shimmer > 0.4:
                    char_buf[sr, sc] = '.' if shimmer < 0.8 else '*'
                    col_buf[sr, sc] = [200, 200, 255]

            # 2. Moon
            moon_c = int(W * 0.80)
            moon_r = max(2, int(H * 0.08))
            for mr, line in enumerate(moon_lines):
                r = moon_r + mr
                if r >= horizon: break
                for mc, ch in enumerate(line):
                    c = moon_c - len(line) // 2 + mc
                    if ch != ' ' and 0 <= c < W:
                        char_buf[r, c] = ch
                        col_buf[r, c] = [255, 250, 230]

            # 3. DISTINCT TEMPLE ARCHITECTURE (Full building, colonnade, arched door, roof)
            # Left Temple (Ubosot)
            temple_c = int(W * 0.19)
            temple_w = int(W * 0.16)
            temple_h = int(H * 0.27)
            wall_h = int(temple_h * 0.42)
            wall_top = horizon - wall_h
            roof_h = temple_h - wall_h

            # Temple Wall & Pillars
            wall_hw = int(temple_w * 0.42)
            for r in range(wall_top, horizon):
                for c in range(temple_c - wall_hw, temple_c + wall_hw + 1):
                    if 0 <= c < W:
                        char_buf[r, c] = '.' if c % 2 == 0 else ':'
                        col_buf[r, c] = [110, 65, 30]

            # Pillars
            for p in range(6):
                pc = (temple_c - wall_hw) + int(p * (wall_hw * 2 / 5.0))
                for r in range(wall_top, horizon):
                    if 0 <= pc < W:
                        char_buf[r, pc] = '|'
                        col_buf[r, pc] = [220, 145, 60]

            # Arched Golden Doorway
            door_h = int(wall_h * 0.75)
            for r in range(horizon - door_h, horizon):
                for dc in range(-2, 3):
                    c = temple_c + dc
                    if 0 <= c < W:
                        char_buf[r, c] = '0'
                        col_buf[r, c] = [255, 215, 90]

            # Three-tiered gabled roofs with chofah
            for tier in range(3):
                t_w = temple_w * (1.0 - tier * 0.22)
                t_h = roof_h * (0.55 + tier * 0.22)
                t_base = wall_top + int(tier * (roof_h * 0.18))
                for dc in range(-int(t_w), int(t_w) + 1):
                    c = temple_c + dc
                    if 0 <= c < W:
                        top_r = t_base - int(math.sqrt(max(0.0, 1.0 - (dc / t_w) ** 2)) * t_h)
                        if 0 <= top_r < horizon:
                            char_buf[top_r, c] = '%' if tier == 2 else '&'
                            col_buf[top_r, c] = [200, 115, 45]
                            if abs(dc) == int(t_w) and top_r - 1 >= 0:
                                char_buf[top_r - 1, c] = '^'
                                col_buf[top_r - 1, c] = [255, 180, 55]

            # Left Bell Stupa
            stupa_c = int(W * 0.07)
            stupa_w = int(W * 0.05)
            stupa_h = int(H * 0.24)
            for r in range(horizon - int(stupa_h * 0.45), horizon):
                norm_y = (r - (horizon - int(stupa_h * 0.45))) / float(stupa_h * 0.45)
                bw = int(stupa_w * math.sin(norm_y * math.pi * 0.75 + 0.25))
                for dc in range(-bw, bw + 1):
                    c = stupa_c + dc
                    if 0 <= c < W:
                        char_buf[r, c] = '8'
                        col_buf[r, c] = [235, 170, 55]
            for sh in range(int(stupa_h * 0.55)):
                r = horizon - int(stupa_h * 0.45) - sh
                if 0 <= r < horizon and 0 <= stupa_c < W:
                    char_buf[r, stupa_c] = '|' if sh % 2 == 0 else '!'
                    col_buf[r, stupa_c] = [255, 215, 75]

            # Right Temple & Pagoda
            r_mount_c = int(W * 0.88)
            r_mount_w = int(W * 0.07)
            r_mount_h = int(H * 0.32)
            for r in range(horizon - int(r_mount_h * 0.45), horizon):
                norm_y = (r - (horizon - int(r_mount_h * 0.45))) / float(r_mount_h * 0.45)
                bw = int(r_mount_w * math.sin(norm_y * math.pi * 0.75 + 0.25))
                for dc in range(-bw, bw + 1):
                    c = r_mount_c + dc
                    if 0 <= c < W:
                        char_buf[r, c] = '8'
                        col_buf[r, c] = [235, 170, 55]
            for sh in range(int(r_mount_h * 0.55)):
                r = horizon - int(r_mount_h * 0.45) - sh
                if 0 <= r < horizon and 0 <= r_mount_c < W:
                    char_buf[r, r_mount_c] = '|' if sh % 2 == 0 else '!'
                    col_buf[r, r_mount_c] = [255, 215, 75]

            # Center Spires
            for off, h_ratio in [(-6, 0.16), (-3, 0.21), (0, 0.28), (3, 0.22), (6, 0.17)]:
                sc = center_x + int(off * (W / 120.0))
                sh = int(H * h_ratio)
                for i in range(sh):
                    r = horizon - sh + i
                    if 0 <= r < horizon and 0 <= sc < W:
                        char_buf[r, sc] = '1' if i < sh - 2 else '|'
                        col_buf[r, sc] = [255, int(180 + (i / sh) * 65), 50]

            # Stone Riverside Embankment
            for c in range(W):
                char_buf[horizon, c] = '='
                col_buf[horizon, c] = [130, 85, 40]
                if c % 7 == 0:
                    char_buf[horizon - 1, c] = '*'
                    col_buf[horizon - 1, c] = [255, 190, 50]

            # 4. Water Base
            for r in range(horizon + 1, H):
                depth = (r - horizon) / max(1, H - horizon)
                for c in range(W):
                    wave = math.sin(c * 0.22 + r * 0.65 + t * 2.8)
                    if wave > 0.42:
                        char_buf[r, c] = '~' if (c + r) % 3 == 0 else '-'
                        col_buf[r, c] = [int(7 + 8 * depth), int(30 + 20 * (1 - depth)), int(18 + 12 * (1 - depth))]

            # 5. TRUE 3D PROJECTION OF COMPACT KRATHONG
            auto_rot_y = t * 0.35
            bob_y = math.sin(t * 2.2) * 0.04
            cam_pitch = 0.44
            cam_dist = 4.6
            fov = min(W, H) * 1.35

            pts = pts_base.copy()
            pts = rot_y(pts, auto_rot_y)
            pts[:, 1] += bob_y
            pts = rot_x(pts, cam_pitch)
            pts[:, 2] += cam_dist

            proj_x = (pts[:, 0] / pts[:, 2]) * fov * 2.0 + center_x
            proj_y = -(pts[:, 1] / pts[:, 2]) * fov + (H * 0.64)
            depths = -pts[:, 2]

            px = proj_x.astype(np.int32)
            py = proj_y.astype(np.int32)

            valid = (px >= 0) & (px < W) & (py >= 0) & (py < H)
            valid_idx = np.where(valid)[0]

            for idx in valid_idx:
                x_p = px[idx]
                y_p = py[idx]
                dep = depths[idx]
                if dep > z_buf[y_p, x_p]:
                    z_buf[y_p, x_p] = dep
                    col = cols_base[idx]
                    mat = mats_base[idx]
                    if mat == 'leaf': ch = '1'
                    elif mat == 'petal_out': ch = '@'
                    elif mat == 'petal_mid': ch = '%'
                    elif mat == 'petal_in': ch = '&'
                    elif mat == 'flower': ch = '8'
                    elif mat == 'candle': ch = '1'
                    else: ch = '#'

                    char_buf[y_p, x_p] = ch
                    col_buf[y_p, x_p] = [int(col[0]), int(col[1]), int(col[2])]

            # 3D Candle Flame
            candle_top = 0.75 + bob_y
            for f in range(20):
                f_phase = (t * 2.5 + f * 0.12) % 1.0
                fy = candle_top + f_phase * 0.40
                fr = 0.05 * (1.0 - f_phase)
                fa = f * 2.4
                fx = math.cos(fa) * fr + math.sin(t * 16) * 0.018 * f_phase
                fz = math.sin(fa) * fr

                cy, sy = math.cos(auto_rot_y), math.sin(auto_rot_y)
                x1 = fx * cy + fz * sy
                z1 = -fx * sy + fz * cy
                y1 = fy

                cx, sx = math.cos(cam_pitch), math.sin(cam_pitch)
                y2 = y1 * cx - z1 * sx
                z2 = y1 * sx + z1 * cx + cam_dist

                cx_scr = int((x1 / z2) * fov * 2.0 + center_x)
                cy_scr = int(-(y2 / z2) * fov + (H * 0.64))

                if 0 <= cx_scr < W and 0 <= cy_scr < H:
                    char_buf[cy_scr, cx_scr] = '1' if f_phase < 0.3 else '*'
                    col_buf[cy_scr, cx_scr] = [255, 235, 80] if f_phase < 0.4 else [255, 110, 20]

            # Water Reflection
            water_line = int(H * 0.63)
            for r in range(water_line, H):
                dist = r - water_line
                src_r = max(0, min(H - 1, water_line - int(dist * 0.72)))
                for c in range(W):
                    if z_buf[r, c] < -9000.0 and char_buf[src_r, c] != ' ':
                        orig_c = col_buf[src_r, c]
                        if np.sum(orig_c) > 100:
                            decay = 1.0 - (dist / float(H - water_line))
                            char_buf[r, c] = '~'
                            col_buf[r, c] = [int(orig_c[0] * 0.5 * decay), int(orig_c[1] * 0.6 * decay + 20), int(orig_c[2] * 0.4 * decay + 15)]

            # Output Frame Buffer with TrueColor ANSI
            lines = []
            for r in range(H):
                row_parts = []
                cur_rgb = (-1, -1, -1)
                for c in range(W):
                    ch = char_buf[r, c]
                    if ch == ' ':
                        row_parts.append(' ')
                        cur_rgb = (-1, -1, -1)
                    else:
                        rgb = tuple(col_buf[r, c])
                        if rgb != cur_rgb:
                            cur_rgb = rgb
                            row_parts.append(f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m")
                        row_parts.append(ch)
                row_parts.append("\033[0m")
                lines.append("".join(row_parts))

            frame_str = "\033[H" + "\n".join(lines)
            sys.stdout.write(frame_str)
            sys.stdout.flush()

            frame_idx += 1
            time.sleep(0.035)

    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[?25h\033[0m\n")
        sys.stdout.flush()

if __name__ == '__main__':
    main()
