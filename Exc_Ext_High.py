import pygame
import sys
import time
import random
import subprocess
import csv
import os
import datetime
import traceback

# ================= 配置区域 =================

# 【A. 核心路径】请修改为您电脑上 Cyberball 可执行文件的实际路径
CYBERBALL_PATH = r"D:\Program\Cyberball\Cyberball-Play.exe"

# 【B. 脚本文件】请确保这个文件与 Cyberball-Play.exe 在同一个文件夹里
CYBERBALL_SCRIPT_NAME = "Standard.cbs"

# 结果数据文件名
DATA_FILENAME = "experiment_data.csv"

# PGG 游戏参数
PGG_ENDOWMENT = 10
PGG_MULTIPLIER = 2
PGG_THRESHOLD = 15  # 【高必要性】门槛：三人总投需达15

# 窗口大小
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800

# 颜色定义
BG_COLOR = (20, 20, 20)
TEXT_COLOR = (255, 255, 255)
BAR_COLOR = (0, 200, 100)
HIGHLIGHT_COLOR = (255, 215, 0)  # 金色
NPC_COLOR = (100, 100, 100)  # 灰色
WARNING_COLOR = (255, 50, 50)  # 红色警示 (用于高必要性)

# --- 全局日志列表 ---
KEY_LOGS = []

# ================= 文案区域 =================

CYBERBALL_INSTRUCTION = """【任务一：网络传球游戏】

接下来，您将参与一个在线互动的传球游戏。
系统将为您随机匹配两名互联网上的其他玩家。

【重要提示】
1. 本游戏需要连接外部服务器，受网络波动影响，连接可能需要几十秒。
2. 连接成功后，请与其他玩家进行互动，点击玩家即为传球，您的投掷数据将被记录。

准备好后，按 [空格键] 开始连接服务器。"""

# 【外部归因反馈】
EXTERNAL_FEEDBACK = """【系统分析报告】

玩家ID：P-2025-EXP-09
任务表现分析：
后台数据显示您获得的传球次数【显著低于】随机概率水平。

原因诊断：外部因素（系统故障/网络波动）
经系统排查，发现实验期间您的客户端存在多次连接延迟和微小的丢包现象。这并非您个人行为风格导致，而是由于实验服务器在该时间段内网络负载过高，随机导致了您与另外两名玩家之间的数据传输出现频道路由问题，从而使得您的互动体验受到了严重限制。"""

PGG_INSTRUCTION_TEXT = f"""【任务二：公共投资决策】

接下来，您将进入第二个任务。
请注意：您将继续与【刚才传球任务中的另外两名玩家】共同完成此游戏。

规则如下：
1. 系统给每人发放 {PGG_ENDOWMENT} 个代币作为初始资金。
2. 您可以选择投入 0 到 {PGG_ENDOWMENT} 个代币到“公共池”中，剩余的留给自己。
3. 公共池中的总金额将【翻 {PGG_MULTIPLIER} 倍】，然后平分给三人。
4. 您的最终收益 = 您保留的金额 + 公共池分红。

【重要提示】
您的最终实验报酬将直接取决于您在本环节的收益总额。
请仔细做出您的决策。"""

# 【高必要性指导语 - 生存模式】
NECESSITY_TEXT_HIGH = f"""【本轮任务模式：生存挑战】

!!! 警告：当前市场环境极其严峻 !!!

补充规则：
1. 本轮投资存在**硬性门槛**：三人投入公共池的总额必须达到【{PGG_THRESHOLD}个代币】。
2. 【后果】：如果总额低于 {PGG_THRESHOLD} 个，公共池将直接**破产清零**，所有投入的资金将被系统没收，无人获得分红！
3. 只有总额达标，才会触发翻倍分红。

为了避免颗粒无收，请务必慎重考虑团队合作。

按 [空格键] 确认并开始决策。"""

# ===========================================

try:
    import pyautogui
except ImportError:
    print("【错误】缺少 pyautogui 库。请运行: pip install pyautogui")
    input("按回车退出...")
    sys.exit()

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Social Interaction Experiment (High Necessity)")
clock = pygame.time.Clock()


def get_font(size):
    """加载中文字体"""
    font_names = ['simhei', 'pingfangsc', 'microsoftyahei', 'stheiti', 'arial']
    for name in font_names:
        try:
            return pygame.font.SysFont(name, size)
        except:
            continue
    return pygame.font.Font(None, size)


def record_event(scene_name, event_key, reaction_time_ms, note=""):
    """记录按键事件"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    log_entry = {
        "Subject_ID": "",
        "Scene": scene_name,
        "Timestamp": timestamp,
        "Reaction_Time_ms": reaction_time_ms,
        "Key": event_key,
        "Note": note
    }
    KEY_LOGS.append(log_entry)


def save_all_data(subject_id, condition_str, investment):
    """保存汇总数据 + 反应时日志"""

    # 1. 保存汇总数据
    file_exists = os.path.isfile(DATA_FILENAME)
    try:
        with open(DATA_FILENAME, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Subject_ID', 'Condition_Group', 'Timestamp', 'PGG_Investment', 'Total_Endowment'])
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([subject_id, condition_str, current_time, investment, PGG_ENDOWMENT])
            print(f">>> 汇总数据已保存: {DATA_FILENAME}")
    except Exception as e:
        print(f"保存结果失败: {e}")

    # 2. 保存详细反应时日志
    log_filename = f"reaction_times_{subject_id}.csv"
    try:
        with open(log_filename, mode='w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ["Subject_ID", "Scene", "Timestamp", "Reaction_Time_ms", "Key", "Note"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for entry in KEY_LOGS:
                entry["Subject_ID"] = subject_id
                writer.writerow(entry)
            print(f">>> 反应时日志已保存: {os.path.abspath(log_filename)}")
    except Exception as e:
        print(f"保存日志失败: {e}")


def draw_text_wrapped(surface, text, color, rect, font, line_spacing=12):
    y = rect.top
    line_height = font.get_height()
    paragraphs = text.split('\n')
    for paragraph in paragraphs:
        current_line = ""
        for char in paragraph:
            test_line = current_line + char
            fw, fh = font.size(test_line)
            if fw < rect.width:
                current_line = test_line
            else:
                surface.blit(font.render(current_line, True, color), (rect.left, y))
                y += line_height + line_spacing
                current_line = char
        if current_line:
            surface.blit(font.render(current_line, True, color), (rect.left, y))
            y += line_height + line_spacing
    return y


def get_user_input(prompt_text):
    """ID 输入框"""
    input_box = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
    color_active = pygame.Color('dodgerblue2')
    text = ''
    font = get_font(32)
    scene_start = pygame.time.get_ticks()
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type == pygame.KEYDOWN:
                rt = pygame.time.get_ticks() - scene_start
                key_name = pygame.key.name(event.key)
                if event.key == pygame.K_RETURN:
                    record_event("ID_Input", "RETURN", rt, f"Confirm: {text}")
                    if len(text) > 0: done = True
                elif event.key == pygame.K_BACKSPACE:
                    record_event("ID_Input", "BACKSPACE", rt, "Delete char")
                    text = text[:-1]
                else:
                    if event.unicode.isalnum():
                        record_event("ID_Input", key_name, rt, f"Type: {event.unicode}")
                        text += event.unicode
        screen.fill(BG_COLOR)
        title_rect = pygame.Rect(100, SCREEN_HEIGHT // 2 - 150, SCREEN_WIDTH - 200, 100)
        draw_text_wrapped(screen, prompt_text, TEXT_COLOR, title_rect, get_font(36))
        txt_surf = font.render(text, True, color_active)
        width = max(200, txt_surf.get_width() + 10)
        input_box.w = width
        input_box.centerx = SCREEN_WIDTH // 2
        screen.blit(txt_surf, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color_active, input_box, 2)
        hint = get_font(24).render("输入后按 [回车] 确认", True, (150, 150, 150))
        screen.blit(hint, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70))
        pygame.display.flip()
        clock.tick(30)
    return text


def scene_posture_instruction(posture_type):
    waiting = True
    scene_start = pygame.time.get_ticks()
    if posture_type == 'defensive':
        title_text = "【任务准备：姿势调整】"
        instruction = "为了标准化实验的生理背景，请在接下来的任务中\n全程保持以下坐姿：\n\n1. 请将 [双臂紧紧交叉] 抱在胸前。\n\n2. 请将 [双腿交叉]（如翘二郎腿或脚踝交叉）。\n\n3. 让身体 [微微前倾并轻微蜷缩]，保持肩膀内收。\n\n请确保在接下来的互动游戏中，始终保持这个姿势，\n直到游戏结束。"
        accent_color = (255, 100, 100)
    else:
        title_text = "【任务准备：姿势调整】"
        instruction = "为了标准化实验的生理背景，请在接下来的任务中\n全程保持以下坐姿：\n\n1. 请以舒适姿势坐好，[背部挺直] 靠在椅背上。\n\n2. 请将 [双手自然平放] 在大腿上。\n\n3. 请将 [双脚平放] 在地面上，不要交叉。\n\n请确保在接下来的互动游戏中，始终保持这个姿势，\n直到游戏结束。"
        accent_color = (100, 255, 100)

    while waiting:
        screen.fill(BG_COLOR)
        title = get_font(40).render(title_text, True, HIGHLIGHT_COLOR)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, int(SCREEN_HEIGHT * 0.1)))
        text_rect = pygame.Rect(int(SCREEN_WIDTH * 0.15), int(SCREEN_HEIGHT * 0.25), int(SCREEN_WIDTH * 0.7),
                                int(SCREEN_HEIGHT * 0.6))
        draw_text_wrapped(screen, instruction, TEXT_COLOR, text_rect, get_font(32), line_spacing=20)
        pygame.draw.rect(screen, accent_color,
                         (int(SCREEN_WIDTH * 0.1), int(SCREEN_HEIGHT * 0.25), 10, int(SCREEN_HEIGHT * 0.5)))
        hint = get_font(24).render("调整好姿势后，按 [空格键] 继续", True, (150, 150, 150))
        screen.blit(hint, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 100))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                rt = pygame.time.get_ticks() - scene_start
                record_event("Posture_Instruction", "SPACE", rt, f"Type: {posture_type}")
                waiting = False


def scene_cyberball_instruction():
    waiting = True
    scene_start = pygame.time.get_ticks()
    text_rect = pygame.Rect(int(SCREEN_WIDTH * 0.15), int(SCREEN_HEIGHT * 0.2), int(SCREEN_WIDTH * 0.7),
                            int(SCREEN_HEIGHT * 0.6))
    while waiting:
        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, (30, 30, 30), text_rect.inflate(40, 40))
        pygame.draw.rect(screen, (100, 100, 255), text_rect.inflate(40, 40), 2)
        draw_text_wrapped(screen, CYBERBALL_INSTRUCTION, TEXT_COLOR, text_rect, get_font(30), line_spacing=15)
        hint = get_font(24).render("按 [空格键] 开始匹配", True, HIGHLIGHT_COLOR)
        screen.blit(hint, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 150))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                rt = pygame.time.get_ticks() - scene_start
                record_event("Cyberball_Instruction", "SPACE", rt, "Start Matching")
                waiting = False


def scene_matching(time_limit=4):
    messages = ["正在连接服务器...", "已连接到节点 CN-East...", "正在搜索玩家...", "匹配成功！建立连接中..."]
    current_msgs = []
    start_y = int(SCREEN_HEIGHT * 0.3)
    for msg in messages:
        screen.fill(BG_COLOR)
        loading_text = get_font(40).render("CONNECTING" + "." * (int(time.time() * 2) % 4), True, (100, 255, 100))
        screen.blit(loading_text, (SCREEN_WIDTH // 2 - 100, int(SCREEN_HEIGHT * 0.15)))
        current_msgs.append(msg)
        y_offset = start_y
        for m in current_msgs:
            text_surf = get_font(28).render(m, True, TEXT_COLOR)
            screen.blit(text_surf, (int(SCREEN_WIDTH * 0.2), y_offset))
            y_offset += 40
        pygame.display.flip()
        time.sleep(random.uniform(0.5, 1.5))
    time.sleep(1)


def scene_ready_to_launch_cyberball(subject_id, condition_id):
    """等待按空格启动 Cyberball"""
    waiting = True
    scene_start = pygame.time.get_ticks()
    while waiting:
        screen.fill(BG_COLOR)
        instruction_text = (
            f"网络连接与匹配已完成！\n\n【重要】请保持当前的坐姿。\n\n在稍后弹出的游戏窗口设置您的 ID ({subject_id}) 和条件 ({condition_id})。\n\n在游戏结束后，关闭弹出窗口以继续。\n\n请按 [空格键] 调出游戏窗口，开始传球任务。")
        text_rect = pygame.Rect(int(SCREEN_WIDTH * 0.15), int(SCREEN_HEIGHT * 0.2), int(SCREEN_WIDTH * 0.7), 400)
        draw_text_wrapped(screen, instruction_text, HIGHLIGHT_COLOR, text_rect, get_font(32), line_spacing=15)
        hint = get_font(24).render("按 [空格键] 调出 Cyberball 窗口", True, (150, 150, 150))
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 100))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                rt = pygame.time.get_ticks() - scene_start
                record_event("Ready_To_Launch", "SPACE", rt, "Launch Cyberball")
                waiting = False
    return True


def launch_cyberball_process_blocking(subject_id, condition_id):
    """启动 Cyberball 并阻塞等待"""
    print("--- Pygame 窗口已关闭，正在启动 Cyberball ---")
    if not os.path.exists(CYBERBALL_PATH):
        print(f"【严重错误】找不到 Cyberball 程序！请检查路径: {CYBERBALL_PATH}")
        input("按回车键跳过 Cyberball 启动...")
        return
    try:
        work_dir = os.path.dirname(CYBERBALL_PATH)
        script_path = os.path.join(work_dir, CYBERBALL_SCRIPT_NAME)
        if os.path.exists(script_path):
            process = subprocess.Popen([CYBERBALL_PATH, script_path], cwd=work_dir)
            print(f">>> 启动 Cyberball 并加载脚本: {CYBERBALL_SCRIPT_NAME}")
        else:
            process = subprocess.Popen([CYBERBALL_PATH], cwd=work_dir)
            print(">>> 启动 Cyberball (未加载脚本)")
        time.sleep(3)
        pyautogui.write(subject_id)
        pyautogui.press('tab')
        time.sleep(0.1)
        pyautogui.write(condition_id)
        process.wait()
        print("--- Cyberball 进程已关闭，继续 Pygame 流程 ---")
    except Exception as e:
        print(f"Cyberball 运行异常: {e}")
        traceback.print_exc()


def scene_loading_results():
    progress = 0
    loading_texts = ["正在上传行为数据...", "正在计算交互频率...", "正在生成个性化报告...", "分析完成"]
    current_text = loading_texts[0]
    bar_width = int(SCREEN_WIDTH * 0.6)
    bar_x = (SCREEN_WIDTH - bar_width) // 2
    bar_y = int(SCREEN_HEIGHT * 0.5)
    while progress <= 100:
        screen.fill(BG_COLOR)
        title = get_font(40).render("系统正在分析您的表现", True, TEXT_COLOR)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, int(SCREEN_HEIGHT * 0.3)))
        if progress < 30:
            current_text = loading_texts[0]
        elif progress < 60:
            current_text = loading_texts[1]
        elif progress < 90:
            current_text = loading_texts[2]
        else:
            current_text = loading_texts[3]
        sub_text = get_font(24).render(current_text, True, (200, 200, 200))
        screen.blit(sub_text, (SCREEN_WIDTH // 2 - sub_text.get_width() // 2, bar_y - 50))
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, 30))
        pygame.draw.rect(screen, BAR_COLOR, (bar_x, bar_y, int(bar_width * (progress / 100)), 30))
        pygame.display.flip()
        progress += random.uniform(0.1, 1.5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
        time.sleep(0.05)


def scene_feedback():
    waiting_for_input = True
    scene_start = pygame.time.get_ticks()
    text_rect = pygame.Rect(int(SCREEN_WIDTH * 0.15), int(SCREEN_HEIGHT * 0.2), int(SCREEN_WIDTH * 0.7),
                            int(SCREEN_HEIGHT * 0.6))
    while waiting_for_input:
        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, (255, 255, 255), text_rect.inflate(60, 60), 2)
        draw_text_wrapped(screen, EXTERNAL_FEEDBACK, TEXT_COLOR, text_rect, get_font(30))
        hint = get_font(24).render("请阅读以上报告，按 [空格键] 继续...", True, (150, 150, 150))
        screen.blit(hint, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 130))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                rt = pygame.time.get_ticks() - scene_start
                record_event("Feedback_Read", "SPACE", rt, "Finish Reading")
                waiting_for_input = False


def scene_call_experimenter():
    waiting = True
    scene_start = pygame.time.get_ticks()
    while waiting:
        screen.fill(BG_COLOR)
        pygame.draw.circle(screen, HIGHLIGHT_COLOR, (SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.3)), 50)
        exclam = get_font(70).render("!", True, BG_COLOR)
        screen.blit(exclam, (SCREEN_WIDTH // 2 - exclam.get_width() // 2, int(SCREEN_HEIGHT * 0.3) - 20))
        title = get_font(40).render("请暂停实验", True, TEXT_COLOR)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, int(SCREEN_HEIGHT * 0.4)))
        msg = "请举手示意主试，并填写纸质问卷。\n\n填写完成后，请主试按 [空格键] 继续实验。"
        text_rect = pygame.Rect(int(SCREEN_WIDTH * 0.2), int(SCREEN_HEIGHT * 0.5), int(SCREEN_WIDTH * 0.6), 300)
        draw_text_wrapped(screen, msg, TEXT_COLOR, text_rect, get_font(32), line_spacing=15)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                rt = pygame.time.get_ticks() - scene_start
                record_event("Call_Experimenter", "SPACE", rt, "Resume Experiment")
                waiting = False


def scene_pgg_instruction():
    waiting_for_input = True
    scene_start = pygame.time.get_ticks()
    text_rect = pygame.Rect(int(SCREEN_WIDTH * 0.15), int(SCREEN_HEIGHT * 0.15), int(SCREEN_WIDTH * 0.7),
                            int(SCREEN_HEIGHT * 0.7))
    while waiting_for_input:
        screen.fill(BG_COLOR)
        draw_text_wrapped(screen, PGG_INSTRUCTION_TEXT, TEXT_COLOR, text_rect, get_font(32), line_spacing=12)
        hint = get_font(24).render("已了解规则，按 [空格键] 继续", True, HIGHLIGHT_COLOR)
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 100))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                rt = pygame.time.get_ticks() - scene_start
                record_event("PGG_Instruction", "SPACE", rt, "Read Rules")
                waiting_for_input = False


def scene_high_necessity_manipulation():
    """
    【高必要性】操纵场景：红色警示，生存模式
    """
    waiting = True
    scene_start = pygame.time.get_ticks()

    # 红色警示色
    border_color = WARNING_COLOR
    text_rect = pygame.Rect(int(SCREEN_WIDTH * 0.2), int(SCREEN_HEIGHT * 0.2), int(SCREEN_WIDTH * 0.6),
                            int(SCREEN_HEIGHT * 0.6))

    while waiting:
        screen.fill(BG_COLOR)

        # 1. 红色背景框
        pygame.draw.rect(screen, (30, 0, 0), text_rect.inflate(40, 40))
        pygame.draw.rect(screen, border_color, text_rect.inflate(40, 40), 4)

        # 2. 标题
        title_surf = get_font(50).render("⚠️ 高风险模式 ⚠️", True, border_color)
        screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, int(SCREEN_HEIGHT * 0.1)))

        # 3. 正文
        draw_text_wrapped(screen, NECESSITY_TEXT_HIGH, TEXT_COLOR, text_rect, get_font(32), line_spacing=15)

        # 4. 底部提示
        hint = get_font(24).render("按 [空格键] 开始投资", True, (150, 150, 150))
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 100))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                rt = pygame.time.get_ticks() - scene_start
                record_event("Necessity_Manip", "SPACE", rt, "Condition: High")
                waiting = False


def draw_avatar(surface, x, y, label, is_active=False):
    color = HIGHLIGHT_COLOR if is_active else NPC_COLOR
    pygame.draw.circle(surface, color, (x, y), 40)
    rect = pygame.Rect(x - 40, y + 10, 80, 60)
    pygame.draw.arc(surface, color, rect, 0, 3.14, 80)
    lbl_s = get_font(24).render(label, True, TEXT_COLOR)
    surface.blit(lbl_s, (x - lbl_s.get_width() // 2, y + 55))


def scene_pgg_game_visual():
    input_text = ""
    error_msg = ""
    error_timer = 0
    font = get_font(32)
    scene_start = pygame.time.get_ticks()

    pos_npc1 = (int(SCREEN_WIDTH * 0.25), int(SCREEN_HEIGHT * 0.3))
    pos_npc2 = (int(SCREEN_WIDTH * 0.75), int(SCREEN_HEIGHT * 0.3))
    pos_you = (int(SCREEN_WIDTH * 0.5), int(SCREEN_HEIGHT * 0.75))

    done = False
    while not done:
        screen.fill(BG_COLOR)
        pygame.draw.line(screen, (50, 50, 50), pos_npc1, pos_npc2, 2)
        pygame.draw.line(screen, (50, 50, 50), pos_npc1, pos_you, 2)
        pygame.draw.line(screen, (50, 50, 50), pos_npc2, pos_you, 2)
        draw_avatar(screen, pos_npc1[0], pos_npc1[1], "Player A")
        draw_avatar(screen, pos_npc2[0], pos_npc2[1], "Player B")
        draw_avatar(screen, pos_you[0], pos_you[1], "You (我)", is_active=True)

        prompt = f"您拥有 {PGG_ENDOWMENT} 代币。请问您要投入公共池多少？"
        prompt_s = get_font(36).render(prompt, True, TEXT_COLOR)
        screen.blit(prompt_s, (SCREEN_WIDTH // 2 - prompt_s.get_width() // 2, int(SCREEN_HEIGHT * 0.1)))

        input_box = pygame.Rect(pos_you[0] - 80, pos_you[1] - 80, 160, 50)
        pygame.draw.rect(screen, (50, 50, 50), input_box)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, input_box, 2)
        txt_surf = font.render(input_text, True, HIGHLIGHT_COLOR)
        screen.blit(txt_surf, (input_box.x + 10, input_box.y + 10))

        if pygame.time.get_ticks() - error_timer < 2000:
            err_surf = get_font(24).render(error_msg, True, WARNING_COLOR)
            screen.blit(err_surf, (SCREEN_WIDTH // 2 - err_surf.get_width() // 2, int(SCREEN_HEIGHT * 0.85)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type == pygame.KEYDOWN:
                rt = pygame.time.get_ticks() - scene_start
                key_name = pygame.key.name(event.key)
                if event.key == pygame.K_RETURN:
                    record_event("PGG_Game", "RETURN", rt, f"Confirm: {input_text}")
                    if len(input_text) > 0:
                        try:
                            val = int(input_text)
                            if 0 <= val <= PGG_ENDOWMENT:
                                done = True
                            else:
                                error_msg = f"请输入 0-{PGG_ENDOWMENT} 的整数"
                                error_timer = pygame.time.get_ticks()
                                input_text = ""
                        except:
                            pass
                elif event.key == pygame.K_BACKSPACE:
                    record_event("PGG_Game", "BACKSPACE", rt, "Delete char")
                    input_text = input_text[:-1]
                else:
                    if event.unicode.isnumeric() and len(input_text) < 2:
                        record_event("PGG_Game", key_name, rt, f"Type: {event.unicode}")
                        input_text += event.unicode
        pygame.display.flip()
        clock.tick(30)
    return int(input_text)


def scene_end():
    screen.fill(BG_COLOR)
    msg = "实验结束，数据已保存。\n请呼唤主试领取报酬。\n\n按 ESC 退出程序。"
    text_rect = pygame.Rect(int(SCREEN_WIDTH * 0.2), int(SCREEN_HEIGHT * 0.4), int(SCREEN_WIDTH * 0.6), 400)
    draw_text_wrapped(screen, msg, TEXT_COLOR, text_rect, get_font(40))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit();
                sys.exit()


def main():
    # 1. 输入 ID
    subject_id = get_user_input("请输入被试编号 (ID):")

    # 2. 条件设置
    cyberball_condition = "1"  # 固定为排斥
    posture_type = 'defensive' if int(subject_id) % 2 != 0 else 'neutral'

    # *** 强制所有人都进入高必要性组 ***
    necessity_type = 'high'

    # --- 阶段一 ---
    scene_posture_instruction(posture_type)
    scene_cyberball_instruction()
    scene_matching()
    scene_ready_to_launch_cyberball(subject_id, cyberball_condition)

    # 退出 Pygame，启动外部程序
    pygame.quit()
    launch_cyberball_process_blocking(subject_id, cyberball_condition)

    # --- 阶段二 ---
    pygame.init()
    global screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Social Interaction Experiment (Feedback)")
    global clock
    clock = pygame.time.Clock()

    scene_loading_results()
    scene_feedback()  # 外部归因
    scene_call_experimenter()
    scene_pgg_instruction()

    # 【高必要性】直接调用高必要性操纵场景
    scene_high_necessity_manipulation()

    investment = scene_pgg_game_visual()

    # 保存数据
    condition_record = f"Cyber{cyberball_condition}_Ext_{posture_type}_{necessity_type}"
    save_all_data(subject_id, condition_record, investment)

    scene_end()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n" + "=" * 40)
        print("【程序崩溃】错误信息如下:")
        traceback.print_exc()
        print("=" * 40)
        input("按回车键关闭窗口...")