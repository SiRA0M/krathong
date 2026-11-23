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
    # Grid Dimensions (64 cols x 48 rows for standard terminal, or auto fit)
    COLS = 64
    ROWS = 48

    # Moon Shape Template
    moon_lines = [
        "   #@0000000@..  ",
        " +0&@000000&0000+",
        "000000000&000000 ",
        "000000&000000000 ",
        "000000000000000  ",
        " &0000000000000  ",
        "  +00000000000   ",
        "    +000000      "
    ]

    # Pre-generate stars
    np.random.seed(42)
    num_stars = 45
    star_x = np.random.randint(0, COLS, size=num_stars)
    star_y = np.random.randint(0, 21, size=num_stars)
    star_chars = np.random.choice([".", "+", "*", "·"], size=num_stars)
    star_speeds = np.random.uniform(1.5, 3.5, size=num_stars)

    # 4 Floating Lanterns in Sky (ซ้ายบน 2, กลางบน 1, ขวากลาง 1)
    lanterns = [
        (17, 7, ["7&8#", "#8*:"]),
        (28, 12, ["488", "1&85"]),
        (33, 4, ["100#", "%&0#*"]),
        (42, 10, ["84&#", "%&0#*"])
    ]

    # Left Building Windows
    left_windows = [
        (20, 2, "%+ %0 #M %+ %% #% MM"),
        (21, 2, "%+ %+ %+ %+ %+ %+ ##")
    ]

    # Water Floating Green Patches
    green_patches = [
        (32, 6, "1111"),
        (40, 3, "111111"),
        (36, 48, "1101"),
        (43, 49, "111111"),
        (42, 56, "&o")
    ]

    # Hide console cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    t0 = time.time()
    frame_idx = 0

    try:
        while True:
            t = time.time() - t0
            term_w, term_h = shutil.get_terminal_size((70, 50))
            W = min(COLS, term_w)
            H = min(ROWS, term_h - 1)
            horizon = int(H * 0.45)
            center_x = int(W * 0.50)

            char_buf = np.full((H, W), ' ', dtype=object)
            col_buf  = np.zeros((H, W, 3), dtype=np.uint8)

            # 1. Sky & Stars
            for i in range(num_stars):
                sc = star_x[i]
                sr = star_y[i]
                if sr < horizon and sc < W:
                    shimmer = math.sin(t * star_speeds[i] + i) * 0.5 + 0.5
                    if shimmer > 0.35:
                        char_buf[sr, sc] = star_chars[i]
                        bright = int(180 + shimmer * 75)
                        col_buf[sr, sc] = [bright, bright, min(255, bright + 15)]

            # 2. Moon (Top Right)
            moon_c = int(W * 0.72)
            moon_r = 3
            for mr, line in enumerate(moon_lines):
                r = moon_r + mr
                if r >= horizon: break
                for mc, ch in enumerate(line):
                    c = moon_c + mc
                    if ch != ' ' and c < W:
                        char_buf[r, c] = ch
                        col_buf[r, c] = [255, 250, 230]

            # 3. 4 Floating Sky Lanterns
            for lx, ly, lines in lanterns:
                l_c = int(lx * (W / COLS))
                l_r = ly
                for l_idx, line in enumerate(lines):
                    r = l_r + l_idx
                    if r < horizon:
                        for ch_idx, ch in enumerate(line):
                            c = l_c + ch_idx
                            if c < W:
                                char_buf[r, c] = ch
                                col_buf[r, c] = [255, 165, 40]

            # 4. Horizon Silhouettes
            # Left Gabled Roof
            gable_c = int(11 * (W / COLS))
            gable_w = 9
            for dx in range(-gable_w, gable_w + 1):
                c = gable_c + dx
                if 0 <= c < W:
                    top_r = horizon - int(math.sqrt(max(0.0, 1.0 - (dx / gable_w) ** 2)) * 7)
                    for r in range(top_r, horizon):
                        if r == top_r or abs(dx) == gable_w:
                            char_buf[r, c] = '%'
                            col_buf[r, c] = [160, 90, 35]

            # Left Windows
            for win_r, win_c, text in left_windows:
                if win_r < H:
                    for i, ch in enumerate(text):
                        c = win_c + i
                        if ch != ' ' and c < W:
                            char_buf[win_r, c] = ch
                            col_buf[win_r, c] = [255, 160, 30]

            # Right Mountain/Pagoda
            mount_c = int(54 * (W / COLS))
            mount_w = 9
            for dx in range(-mount_w, mount_w + 1):
                c = mount_c + dx
                if 0 <= c < W:
                    top_r = horizon - int((1.0 - abs(dx) / mount_w) ** 1.8 * 11)
                    for r in range(top_r, horizon):
                        if r == top_r or abs(dx) == mount_w:
                            char_buf[r, c] = '#'
                            col_buf[r, c] = [140, 75, 30]

            # Center Spires & Intense Golden Light
            for sp_c, sp_h in [(center_x - 1, 5), (center_x, 8), (center_x + 1, 6)]:
                for i in range(sp_h):
                    r = horizon - sp_h + i
                    if 0 <= r < horizon and 0 <= sp_c < W:
                        char_buf[r, sp_c] = '1' if i < sp_h - 2 else '|'
                        col_buf[r, sp_c] = [255, 210, 60]

            # 5. Deep Dark Green Water Base (ผิวน้ำสีเขียวเข้มเกือบดำ)
            for r in range(horizon + 1, H):
                depth = (r - horizon) / max(1, H - horizon)
                for c in range(W):
                    wave = math.sin(c * 0.28 + r * 0.70 + t * 2.8)
                    if wave > 0.45:
                        char_buf[r, c] = '~' if (c + r) % 3 == 0 else '-'
                        col_buf[r, c] = [int(6 + 6 * depth), int(28 + 16 * (1 - depth)), int(16 + 10 * (1 - depth))]
                    elif wave < -0.55:
                        char_buf[r, c] = '/'
                        col_buf[r, c] = [4, 18, 12]

            # 6. Center Glowing Orb (Upper Orange/Pink/Gold, Lower Lime Green)
            orb_r = horizon + 3
            orb_rx = int(14 * (W / COLS))
            orb_ry = 5
            for dy in range(-orb_ry, orb_ry + 1):
                r = orb_r + dy
                if r < horizon or r >= H: continue
                for dx in range(-orb_rx, orb_rx + 1):
                    c = center_x + dx
                    if 0 <= c < W:
                        dist = math.sqrt((dx / orb_rx) ** 2 + (dy / orb_ry) ** 2)
                        if dist <= 1.0:
                            if dy > 1 or dist > 0.75:
                                # Lower Lime Green rim
                                char_buf[r, c] = '1' if (dx + dy) % 2 == 0 else '0'
                                col_buf[r, c] = [120, 220, 30]
                            elif dy < 0 and dist > 0.35:
                                # Upper Pink/Orange/Gold
                                char_buf[r, c] = '@' if dx % 2 == 0 else '#'
                                col_buf[r, c] = [255, 140, 165]
                            else:
                                # Radiant White-Gold Core
                                char_buf[r, c] = '0' if (dx * dy) % 2 == 0 else '&'
                                col_buf[r, c] = [255, 250, 215]

            # Soft Vertical Reflection Below
            refl_start = orb_r + orb_ry
            for dy in range(12):
                r = refl_start + dy
                if r >= H: break
                prog = dy / 12.0
                wave_shift = int(math.sin(dy * 0.5 + t * 3.5) * 1.8)
                spread = int(orb_rx * (1.0 - prog * 0.5))
                for dx in range(-spread, spread + 1):
                    c = center_x + dx + wave_shift
                    if 0 <= c < W and (c + r + frame_idx) % 3 != 0:
                        decay = (1.0 - prog * 0.8)
                        char_buf[r, c] = '|' if dx == 0 else '~'
                        col_buf[r, c] = [int(180 * decay), int(190 * decay), int(50 * decay)]

            # Bottom-left Green Patches
            for pr, pc, ptxt in green_patches:
                if pr < H:
                    for k, ch in enumerate(ptxt):
                        c = pc + k
                        if c < W:
                            char_buf[pr, c] = ch
                            col_buf[pr, c] = [110, 240, 85]

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
