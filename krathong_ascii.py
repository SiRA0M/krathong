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
    # Moon shape template
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

    # Pre-generate stars
    np.random.seed(42)
    max_stars = 150
    star_x = np.random.rand(max_stars)
    star_y = np.random.rand(max_stars) * 0.44
    star_chars = np.random.choice([".", "+", "*", "·", "'"], size=max_stars)
    star_speeds = np.random.uniform(1.2, 3.2, size=max_stars)

    # Sky Lanterns (Widescreen multi-point)
    lantern_data = [
        (0.17, 0.18, ["7&8#", "#8*:"]),
        (0.28, 0.28, ["488", "1&85"]),
        (0.50, 0.12, ["100#", "%&0#*", "9&8"]),
        (0.63, 0.22, ["84&#", "%&0#*", "7#"]),
        (0.08, 0.24, ["8#", "*:"]),
        (0.38, 0.20, ["88", "1&"]),
        (0.74, 0.30, ["40#", "98"]),
        (0.88, 0.16, ["80", "*"])
    ]

    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

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
            krathong_y = int(H * 0.53)

            char_buf = np.full((H, W), ' ', dtype=object)
            col_buf  = np.zeros((H, W, 3), dtype=np.uint8)

            # 1. Sky & Stars
            num_s = int(W * 0.75)
            for i in range(min(num_s, max_stars)):
                sc = int(star_x[i] * W)
                sr = int(star_y[i] * H)
                if sr < horizon and 0 <= sc < W:
                    shimmer = math.sin(t * star_speeds[i] + i) * 0.5 + 0.5
                    if shimmer > 0.3:
                        char_buf[sr, sc] = star_chars[i]
                        bright = int(175 + shimmer * 80)
                        col_buf[sr, sc] = [bright, bright, min(255, bright + 15)]

            # 2. Detailed Moon (Top Right)
            moon_c = int(W * 0.78)
            moon_r = max(2, int(H * 0.08))
            for mr, line in enumerate(moon_lines):
                r = moon_r + mr
                if r >= horizon: break
                for mc, ch in enumerate(line):
                    c = moon_c - len(line) // 2 + mc
                    if ch != ' ' and 0 <= c < W:
                        char_buf[r, c] = ch
                        col_buf[r, c] = [255, 250, 230]

            # 3. Sky Lanterns
            for lx, ly, lines in lantern_data:
                cur_x = (lx + t * 0.002) % 1.0
                cur_y = ((ly - t * 0.012) % 0.44 + 0.44) % 0.44
                l_c = int(cur_x * W)
                l_r = int(cur_y * H)
                for l_idx, line in enumerate(lines):
                    r = l_r + l_idx
                    if 0 <= r < horizon:
                        for ch_idx, ch in enumerate(line):
                            c = l_c + ch_idx - len(line) // 2
                            if 0 <= c < W:
                                char_buf[r, c] = ch
                                col_buf[r, c] = [255, 168, 45]

            # 4. Temple Architecture
            # Left Grand Royal Temple with illuminated windows
            temple_c = int(W * 0.18)
            temple_w = int(W * 0.12)
            for dc in range(-temple_w, temple_w + 1):
                c = temple_c + dc
                if 0 <= c < W:
                    h_prog = math.sqrt(max(0.0, 1.0 - (dc / temple_w) ** 2))
                    top_r = horizon - int(h_prog * (H * 0.20))
                    for r in range(top_r, horizon):
                        if r == top_r or abs(dc) == temple_w:
                            char_buf[r, c] = '%'
                            col_buf[r, c] = [175, 105, 40]

            # Golden windows
            win_text = "%+  %0  #M  %+  %%  #%  MM"
            for row_off in [3, 1]:
                wr = horizon - row_off
                start_wc = temple_c - len(win_text) // 2
                for idx, ch in enumerate(win_text):
                    c = start_wc + idx
                    if ch != ' ' and 0 <= c < W and wr >= 0:
                        char_buf[wr, c] = ch
                        col_buf[wr, c] = [255, 160, 35]

            # Left Stupa
            stupa_c = int(W * 0.07)
            for dc in range(-int(W * 0.05), int(W * 0.05) + 1):
                c = stupa_c + dc
                if 0 <= c < W:
                    top_r = horizon - int((1.0 - abs(dc) / (W * 0.05)) ** 1.9 * (H * 0.18))
                    for r in range(top_r, horizon):
                        if r == top_r or abs(dc) == int(W * 0.05):
                            char_buf[r, c] = '#'
                            col_buf[r, c] = [160, 95, 38]

            # Right Mountain & Chedi
            mount_c = int(W * 0.88)
            mount_w = int(W * 0.09)
            for dc in range(-mount_w, mount_w + 1):
                c = mount_c + dc
                if 0 <= c < W:
                    top_r = horizon - int((1.0 - abs(dc) / mount_w) ** 1.8 * (H * 0.28))
                    for r in range(top_r, horizon):
                        if r == top_r or abs(dc) == mount_w:
                            char_buf[r, c] = '#'
                            col_buf[r, c] = [140, 75, 30]

            # Center Wat Arun Spires & Radial Light
            spire_offsets = [(-6, 0.14), (-3, 0.19), (0, 0.26), (3, 0.20), (6, 0.15)]
            for off, h_ratio in spire_offsets:
                sc = center_x + int(off * (W / 120.0))
                sh = int(H * h_ratio)
                for i in range(sh):
                    r = horizon - sh + i
                    if 0 <= r < horizon and 0 <= sc < W:
                        char_buf[r, sc] = '1' if i < sh - 2 else '|'
                        col_buf[r, sc] = [255, int(180 + (i / sh) * 65), 50]

            # Horizon line
            for c in range(W):
                if char_buf[horizon, c] == ' ':
                    char_buf[horizon, c] = '-'
                    col_buf[horizon, c] = [60, 45, 25]

            # 5. Deep Dark Green Water
            for r in range(horizon + 1, H):
                depth = (r - horizon) / max(1, H - horizon)
                for c in range(W):
                    wave = math.sin(c * 0.22 + r * 0.65 + t * 2.8)
                    if wave > 0.42:
                        char_buf[r, c] = '~' if (c + r) % 3 == 0 else '-'
                        col_buf[r, c] = [int(7 + 8 * depth), int(30 + 20 * (1 - depth)), int(18 + 12 * (1 - depth))]
                    elif wave < -0.60:
                        char_buf[r, c] = '/'
                        col_buf[r, c] = [5, 20, 12]

            # 6. Detailed Krathong
            kw = int(W * 0.20)
            kh = int(H * 0.11)
            bob = math.sin(t * 2.4) * 0.5
            kr_y = krathong_y + int(bob)

            # Outer folded leaf points
            num_leaves = 16
            for leaf in range(num_leaves):
                ang = (leaf / num_leaves) * math.pi * 2
                cos_a, sin_a = math.cos(ang), math.sin(ang)
                dc = int(cos_a * kw * 1.05)
                dr = int(sin_a * kh * 1.05)
                c = center_x + dc
                r = kr_y + dr
                if horizon < r < H and 0 <= c < W:
                    char_buf[r, c] = '^'
                    col_buf[r, c] = [135, 230, 35]

            # Multi-tiered petals
            for dy in range(-kh, kh + 1):
                r = kr_y + dy
                if r <= horizon or r >= H: continue
                for dx in range(-kw, kw + 1):
                    c = center_x + dx
                    if 0 <= c < W:
                        norm_d = math.sqrt((dx / kw) ** 2 + (dy / kh) ** 2)
                        if norm_d <= 1.0:
                            if dy > kh * 0.30 or norm_d > 0.80:
                                # Banana leaf green rim
                                char_buf[r, c] = '1' if (dx + dy) % 2 == 0 else '0'
                                col_buf[r, c] = [140, 225, 30]
                            elif norm_d > 0.55:
                                # Outer lotus pink
                                char_buf[r, c] = '@' if dx % 2 == 0 else '#'
                                col_buf[r, c] = [255, int(115 + math.sin(dx * 0.5) * 35), 175]
                            elif norm_d > 0.32:
                                # Inner marigold gold
                                char_buf[r, c] = '8' if dy % 2 == 0 else '%'
                                col_buf[r, c] = [255, 195, 60]
                            else:
                                # Radiant core
                                char_buf[r, c] = '0' if (dx * dy) % 2 == 0 else '&'
                                col_buf[r, c] = [255, 252, 220]

            # Incense Sticks
            for off_x in [-2, 0, 2]:
                for ih in range(int(kh * 1.4)):
                    r = kr_y - int(kh * 0.3) - ih
                    c = center_x + off_x
                    if 0 <= r < H and 0 <= c < W:
                        char_buf[r, c] = '*' if ih == int(kh * 1.4) - 1 else '|'
                        col_buf[r, c] = [255, 120, 30] if ih == int(kh * 1.4) - 1 else [170, 85, 50]

            # Candle & Flame
            candle_h = int(kh * 1.1)
            for ch in range(candle_h):
                r = kr_y - int(kh * 0.2) - ch
                for fdc in [-1, 0, 1]:
                    c = center_x + fdc
                    if 0 <= r < H and 0 <= c < W:
                        char_buf[r, c] = '1'
                        col_buf[r, c] = [255, 245, 190]

            flame_h = int(H * 0.15)
            flicker = math.sin(t * 16.0) * 0.7
            for fh in range(flame_h + 1):
                r = kr_y - int(kh * 0.2) - candle_h - fh
                if r < 0 or r >= H: continue
                prog = fh / flame_h
                spread = max(0, int((1.0 - prog) * 2.5))
                for fdc in range(-spread, spread + 1):
                    c = center_x + fdc + int(flicker * prog)
                    if 0 <= c < W:
                        if prog < 0.25:
                            char_buf[r, c] = '1' if fdc == 0 else '!'
                            col_buf[r, c] = [255, 255, 235]
                        elif prog < 0.65:
                            char_buf[r, c] = '1' if fdc == 0 else '|'
                            col_buf[r, c] = [255, 205, 55]
                        else:
                            char_buf[r, c] = '*'
                            col_buf[r, c] = [255, 110, 20]

            # 7. Water Reflection
            refl_start = kr_y + kh
            max_refl = int(H * 0.35)
            for dy in range(max_refl):
                r = refl_start + dy
                if r >= H: break
                prog = dy / float(max_refl)
                wave_shift = int(math.sin(dy * 0.4 + t * 3.8) * 2.8)
                spread = int(kw * (1.0 - prog * 0.52))
                for dx in range(-spread, spread + 1):
                    c = center_x + dx + wave_shift
                    if 0 <= c < W and (c + r + frame_idx) % 4 != 0:
                        decay = (1.0 - prog * 0.85)
                        char_buf[r, c] = '|' if dx == 0 else '~'
                        col_buf[r, c] = [int(200 * decay), int(210 * decay), int(60 * decay)]

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
