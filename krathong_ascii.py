import math
import os
import sys
import time
import shutil
import numpy as np

# Enable Windows ANSI Virtual Terminal Processing
if os.name == 'nt':
    os.system('')

def main():
    # Character palettes matching the original artwork
    dense_chars = ["@", "%", "#", "&", "8", "0", "W", "B", "M"]
    mid_chars   = ["o", "*", "=", "+", "a", "e", "s", "1", "0"]
    water_chars = ["~", "-", "=", "_", "≈"]

    # Pre-generate stars
    np.random.seed(42)
    num_stars = 75
    star_x = np.random.rand(num_stars)
    star_y = np.random.rand(num_stars) * 0.42
    star_chars = np.random.choice(["+", "*", "·", "o"], size=num_stars)
    star_speeds = np.random.uniform(1.5, 3.5, size=num_stars)

    # Hide console cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    t0 = time.time()
    frame_idx = 0

    try:
        while True:
            t = time.time() - t0
            term_w, term_h = shutil.get_terminal_size((90, 42))
            W = max(60, min(130, term_w))
            H = max(26, min(55, term_h - 1))

            horizon = int(H * 0.44)
            center_x = int(W * 0.50)
            krathong_y = int(H * 0.47)

            # Character and Color Buffers
            char_buf = np.full((H, W), ' ', dtype=object)
            col_buf  = np.zeros((H, W, 3), dtype=np.uint8)

            # 1. Sky & Twinkling Stars
            for i in range(num_stars):
                sc = int(star_x[i] * W)
                sr = int(star_y[i] * H)
                if sr < horizon and 0 <= sc < W:
                    shimmer = math.sin(t * star_speeds[i] + i) * 0.5 + 0.5
                    if shimmer > 0.35:
                        char_buf[sr, sc] = star_chars[i]
                        bright = int(180 + shimmer * 75)
                        col_buf[sr, sc] = [bright, bright, 255]

            # 2. Full Moon (Top Right)
            moon_x = int(W * 0.78)
            moon_y = int(H * 0.15)
            moon_rx = int(W * 0.09)
            moon_ry = int(H * 0.08)

            for dy in range(-moon_ry * 2, moon_ry * 2 + 1):
                r = moon_y + dy
                if r < 0 or r >= horizon: continue
                for dx in range(-moon_rx * 2, moon_rx * 2 + 1):
                    c = moon_x + dx
                    if c < 0 or c >= W: continue
                    dist = math.sqrt((dx / moon_rx) ** 2 + (dy / moon_ry) ** 2)
                    if dist <= 1.0:
                        char_buf[r, c] = dense_chars[(abs(dx * 3 + dy * 5) + frame_idx // 3) % len(dense_chars)]
                        intensity = 1.0 - dist * 0.25
                        col_buf[r, c] = [int(255 * intensity), int(245 * intensity), int(210 * intensity)]
                    elif dist <= 1.5 and ((dx + dy) % 2 == 0):
                        char_buf[r, c] = '·'
                        col_buf[r, c] = [180, 150, 90]

            # 3. Pagoda / Temple Silhouette on Horizon
            # Left Stupa Dome
            dome_x = int(W * 0.20)
            dome_rx = int(W * 0.14)
            dome_ry = int(H * 0.15)
            for dx in range(-dome_rx, dome_rx + 1):
                c = dome_x + dx
                if 0 <= c < W:
                    h_norm = math.sqrt(max(0.0, 1.0 - (dx / dome_rx) ** 2))
                    top_r = horizon - int(h_norm * dome_ry)
                    for r in range(top_r, horizon):
                        if r == top_r or abs(dx) == dome_rx:
                            char_buf[r, c] = '%'
                            col_buf[r, c] = [180, 110, 45]
                        elif r == horizon - 1 and c % 2 == 0:
                            char_buf[r, c] = '#'
                            col_buf[r, c] = [150, 90, 35]

            # Right Temple Spires
            spire_x = int(W * 0.86)
            spire_w = int(W * 0.11)
            for dx in range(-spire_w, spire_w + 1):
                c = spire_x + dx
                if 0 <= c < W:
                    h_norm = max(0.0, 1.0 - abs(dx) / spire_w)
                    top_r = horizon - int((h_norm ** 1.6) * (H * 0.22))
                    for r in range(top_r, horizon):
                        if r == top_r or abs(dx) == spire_w:
                            char_buf[r, c] = '#'
                            col_buf[r, c] = [190, 120, 50]

            # Horizon line
            for c in range(W):
                char_buf[horizon, c] = '-'
                col_buf[horizon, c] = [70, 50, 35]

            # 4. Floating Lanterns (โคมลอย)
            lant_configs = [
                (0.28, 0.22, ["488", "1&85"], 0.012),
                (0.16, 0.15, ["7&8#", "#8*:"], 0.015),
                (0.52, 0.10, ["100#", "%&0#*"], 0.011),
                (0.63, 0.18, ["84&#", "%&0#*"], 0.014)
            ]
            for lx, ly, lines, spd in lant_configs:
                cur_y = ((ly - t * spd) % 0.42 + 0.42) % 0.42
                l_c = int(lx * W)
                l_r = int(cur_y * H)
                for l_idx, line in enumerate(lines):
                    r = l_r + l_idx
                    if 0 <= r < horizon:
                        for ch_idx, ch in enumerate(line):
                            c = l_c + ch_idx - len(line) // 2
                            if 0 <= c < W:
                                char_buf[r, c] = ch
                                col_buf[r, c] = [255, 185, 75]

            # 5. Blue Water Matrix (ผิวน้ำสีฟ้าทั้งครึ่งล่าง)
            for r in range(horizon + 1, H):
                depth = (r - horizon) / max(1, H - horizon)
                for c in range(W):
                    wave = math.sin(c * 0.25 + r * 0.65 + t * 3.0)
                    if wave > 0.45:
                        char_buf[r, c] = '~' if (c + r) % 3 == 0 else '-'
                        col_buf[r, c] = [int(12 + 10 * depth), int(45 + 50 * (1 - depth)), int(85 + 75 * (1 - depth))]
                    elif wave < -0.6:
                        char_buf[r, c] = '/'
                        col_buf[r, c] = [8, 30, 55]

            # 6. Center Krathong Body
            kw = int(W * 0.26)
            kh = int(H * 0.10)
            bob = math.sin(t * 2.5) * 0.5
            kr_y = krathong_y + int(bob)

            for dy in range(-kh, kh + 1):
                r = kr_y + dy
                if r < 0 or r >= H: continue
                for dx in range(-kw, kw + 1):
                    c = center_x + dx
                    if c < 0 or c >= W: continue
                    dist_sq = (dx / kw) ** 2 + (dy / kh) ** 2
                    if dist_sq <= 1.0:
                        dist = math.sqrt(dist_sq)
                        if dist > 0.68:
                            # Green Banana leaves (กลีบตองสีเขียว 1, 0, &, 8, %)
                            char_buf[r, c] = mid_chars[(abs(dx * 5 + dy * 7) + frame_idx // 2) % len(mid_chars)]
                            col_buf[r, c] = [int(135 - dist * 35), int(210 - dist * 25), 40]
                        elif dist > 0.45:
                            # Pink Lotus Petals (กลีบบัวสีชมพู)
                            char_buf[r, c] = dense_chars[(abs(dx * 7 + dy * 11) + frame_idx // 3) % len(dense_chars)]
                            col_buf[r, c] = [245, int(120 + math.sin(dx) * 30), 175]
                        else:
                            # Radiant Core (แกนดอกบัวสีทองสว่าง)
                            char_buf[r, c] = dense_chars[(abs(dx * 3 + dy * 5) + frame_idx // 4) % len(dense_chars)]
                            col_buf[r, c] = [255, 245, 190]

            # Candle Flame (เปลวเทียนตรงกลางสั่นไหว)
            flame_h = int(H * 0.17)
            flicker = math.sin(t * 16.0) * 0.6
            for fh in range(flame_h + 1):
                r = kr_y - int(kh * 0.5) - fh
                if r < 0 or r >= H: continue
                prog = fh / flame_h
                spread = max(0, int((1.0 - prog) * 2.2))
                for fdx in range(-spread, spread + 1):
                    c = center_x + fdx + int(flicker * prog)
                    if 0 <= c < W:
                        if prog < 0.3:
                            char_buf[r, c] = '1' if fdx == 0 else '!'
                            col_buf[r, c] = [255, 255, 230]
                        elif prog < 0.7:
                            char_buf[r, c] = '1' if fdx == 0 else '|'
                            col_buf[r, c] = [255, 200, 60]
                        else:
                            char_buf[r, c] = '*'
                            col_buf[r, c] = [255, 100, 20]

            # 7. Giant Water Reflection (เงาสะท้อนทอดยาวลงผิวน้ำ)
            refl_start = kr_y + kh
            max_refl = int(H * 0.40)
            for dy in range(max_refl):
                r = refl_start + dy
                if r >= H: break
                refl_prog = dy / max_refl
                wave_shift = int(math.sin(dy * 0.4 + t * 4.2) * 3.2)
                src_r = max(kr_y - kh, kr_y + int(kh * 0.5) - int(dy * 0.5))
                spread = int(kw * (1.0 - refl_prog * 0.45))

                for dx in range(-spread, spread + 1):
                    c = center_x + dx + wave_shift
                    if c < 0 or c >= W: continue
                    if (c + r + frame_idx) % 4 == 0: continue
                    sc = center_x + dx
                    if 0 <= sc < W and char_buf[src_r, sc] != ' ':
                        orig_c = col_buf[src_r, sc]
                        decay = (1.0 - refl_prog * 0.75)
                        char_buf[r, c] = '|' if dx == 0 else ('~' if (r + c) % 2 == 0 else '=')
                        col_buf[r, c] = [
                            int(min(255, orig_c[0] * 0.65 * decay)),
                            int(min(255, (orig_c[1] * 0.70 + 30) * decay)),
                            int(min(255, (orig_c[2] * 0.60 + 80) * decay))
                        ]

            # 8. Floating Water Sparkles (กลุ่มดอกไม้/พิกเซลลอยน้ำ 111111, &o)
            sparkles = [
                (0.18, 0.54, "1111"), (0.11, 0.70, "111111"),
                (0.75, 0.62, "1101"), (0.76, 0.74, "111111"),
                (0.88, 0.88, "&o"), (0.32, 0.91, "00")
            ]
            for sx, sy, stxt in sparkles:
                sr = int(sy * H)
                sc = int(sx * W)
                if sr < H:
                    for k, ch in enumerate(stxt):
                        c = sc + k
                        if 0 <= c < W:
                            char_buf[sr, c] = ch
                            col_buf[sr, c] = [90, 230, 110]

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
            time.sleep(0.04)

    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[?25h\033[0m\n")
        sys.stdout.flush()

if __name__ == '__main__':
    main()
