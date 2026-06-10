import pygame
import random

# 游戏参数
SCREEN_WIDTH = 240  # 游戏窗口宽度
SCREEN_HEIGHT = 240  # 游戏窗口高度
BLOCK_SIZE = 30  # 每个方块的尺寸
GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE  # 网格宽度（8列）
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE  # 网格高度（8行）
FPS = 10  # 设置帧率
CLEAR_DELAY = 1000 # 消除后的延迟时间（毫秒）改为1秒

# 定义颜色（保持原有颜色定义不变）
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PURPLE = (128, 0, 128)
TURQUOISE = (64, 224, 208)

# 定义俄罗斯方块形状及其颜色（保持原有形状定义不变）
SHAPES = [
    [[1, 1, 1, 1]],  # I形
    [[1, 1, 0], [0, 1, 1]],  # Z形
    [[0, 1, 1], [1, 1, 0]],  # S形
    [[1, 1], [1, 1]],  # O形
    [[1, 1, 1], [0, 1, 0]],  # T形
    [[0, 0, 1], [1, 1, 1]],  # L形
    [[1, 0, 0], [1, 1, 1]],  # J形
]

SHAPE_COLORS = [
    (255, 255, 151),  # I形
    (117, 117, 209),  # Z形
    (87, 211, 255),  # S形
    (178, 222, 30),  # O形
    (158, 211, 215),  # T形
    (255, 79, 79),  # L形
    (255, 205, 47),  # J形
]


class Tetris:
    def __init__(self):
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.game_over = False
        self.current_shape = None
        self.current_color = None
        self.x = 0
        self.y = 0
        self.shape_counter = 0
        self.fall_time = 0
        self.speed = 1200
        self.level = 1
        self.move_speed = 1
        self.last_move_time = 0
        self.move_delay = 200
        self.vanishing_blocks = []
        self.pending_clear_lines = []  # 新增：待清除的行
        self.clear_start_time = 0  # 新增：清除开始时间
        self.is_clearing = False
        self.is_new_shape_delayed = False  # 新增：新方块延迟标志
        self.new_shape_delay_time = 0  # 新增：新方块延迟时间
        self.fall_row_start_time = 0  # 新增：行下落延迟开始时间
        self.pending_fall_rows = False  # 新增：需要处理行下落

    def new_shape(self):
        # 修改方块生成顺序，按照 T → Z → I → O → J → S → L 的顺序
        shape_order = [4, 1, 0, 3, 6, 2, 5]
        shape_index = shape_order[self.shape_counter % len(shape_order)]
        self.current_shape = SHAPES[shape_index]
        self.current_color = SHAPE_COLORS[shape_index]
        self.x = GRID_WIDTH // 2 - len(self.current_shape[0]) // 2
        self.y = 0
        self.shape_counter += 1
        # 设置新方块延迟
        self.is_new_shape_delayed = True
        self.new_shape_delay_time = pygame.time.get_ticks()

    # 碰撞检测（保持原有逻辑不变）
    def collide(self):
        for i, row in enumerate(self.current_shape):
            for j, cell in enumerate(row):
                if cell:
                    if (self.x + j < 0 or self.x + j >= len(self.board[0]) or
                            self.y + i >= len(self.board) or self.board[self.y + i][self.x + j]):
                        return True
        return False

    def freeze(self):
        if self.is_clearing:
            return
        # 冻结方块时立即更新到面板
        for i, row in enumerate(self.current_shape):
            for j, cell in enumerate(row):
                if cell:
                    self.board[self.y + i][self.x + j] = self.current_color
        self.clear_lines()
        if not self.is_clearing:  # 如果没有需要清除的行则立即生成新方块
            self.new_shape()

    def clear_lines(self):
        full_lines = []
        # 检测满行
        for i, row in enumerate(self.board):
            if all(cell != 0 for cell in row):
                full_lines.append(i)

        if full_lines:
            self.is_clearing = True
            self.clear_start_time = pygame.time.get_ticks()
            self.pending_clear_lines = full_lines

            # 记录消失动画
            for line in full_lines:
                for j in range(len(self.board[line])):
                    color = self.board[line][j]
                    if color != 0:
                        self.vanishing_blocks.append({
                            'x': j * BLOCK_SIZE,
                            'y': line * BLOCK_SIZE,
                            'color': color,
                            'alpha': 255
                        })

    def rotate(self):
        if self.is_clearing or self.is_new_shape_delayed:
            return
        rotated = list(zip(*self.current_shape[::-1]))
        if self.valid_position(rotated):
            self.current_shape = rotated

    def valid_position(self, shape=None):
        if shape is None:
            shape = self.current_shape
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    if (self.x + j < 0 or self.x + j >= len(self.board[0]) or
                            self.y + i >= len(self.board) or self.board[self.y + i][self.x + j]):
                        return False
        return True

    # 移动控制（保持原有逻辑不变）
    def move_left(self):
        if self.is_clearing or self.is_new_shape_delayed:
            return
        self.x -= 1
        if self.collide():
            self.x += 1

    def move_right(self):
        if self.is_clearing or self.is_new_shape_delayed:
            return
        self.x += 1
        if self.collide():
            self.x -= 1

    def move_down(self):
        if self.is_clearing or self.is_new_shape_delayed:
            return
        self.y += 1
        if self.collide():
            self.y -= 1
            self.freeze()

    def draw(self, screen):
        screen.fill(BLACK)
        # 绘制网格线（保持原有逻辑不变）
        for i in range(GRID_HEIGHT):
            pygame.draw.line(screen, (169, 169, 169), (0, i * BLOCK_SIZE), (SCREEN_WIDTH, i * BLOCK_SIZE))
        for i in range(GRID_WIDTH):
            pygame.draw.line(screen, (169, 169, 169), (i * BLOCK_SIZE, 0), (i * BLOCK_SIZE, SCREEN_HEIGHT))

        # 绘制固定方块（排除待清除行）
        for i, row in enumerate(self.board):
            if i not in self.pending_clear_lines:  # 新增：不绘制待清除行
                for j, color in enumerate(row):
                    if color != 0:
                        pygame.draw.rect(screen, color, (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        # 绘制当前方块（保持原有逻辑）
        if not self.is_clearing and not self.is_new_shape_delayed:
            for i, row in enumerate(self.current_shape):
                for j, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(screen, self.current_color,
                                         ((self.x + j) * BLOCK_SIZE, (self.y + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        # 绘制消失动画（保持原有逻辑）
        for block in self.vanishing_blocks[:]:
            alpha = block['alpha']
            if alpha <= 0:
                self.vanishing_blocks.remove(block)
                continue
            surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
            surf.fill((*block['color'], alpha))
            screen.blit(surf, (block['x'], block['y']))

        # 游戏结束文字（保持原有逻辑）
        if self.game_over:
            font = pygame.font.SysFont(None, 50)
            game_over_text = font.render("GAME OVER", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
        pygame.display.update()

    def check_game_over(self):
        for col in self.board[0]:
            if col != 0:
                self.game_over = True

    def increase_level(self):
        if self.level * 500 <= self.shape_counter:
            self.level += 1
            self.speed -= 50

    def update_fall_time(self):
        if self.is_clearing:
            return
        # 处理新方块延迟
        if self.is_new_shape_delayed:
            if pygame.time.get_ticks() - self.new_shape_delay_time >= 1000:
                self.is_new_shape_delayed = False
            else:
                return  # 在延迟期内，不自动下落
        now = pygame.time.get_ticks()
        if now - self.fall_time >= self.speed:
            self.fall_time = now
            self.move_down()

    def update_animation(self):
        # 处理消除延迟
        if self.is_clearing:
            current_time = pygame.time.get_ticks()
            if current_time - self.clear_start_time >= CLEAR_DELAY:
                # 执行实际的消除和下落
                full_lines_sorted = sorted(self.pending_clear_lines, reverse=True)
                for line in full_lines_sorted:
                    self.board.pop(line)
                for _ in range(len(full_lines_sorted)):
                    self.board.insert(0, [0 for _ in range(GRID_WIDTH)])
                self.is_clearing = False
                self.pending_clear_lines = []
                self.new_shape()  # 生成新方块并启动延迟
                # 设置行下落延迟
                self.fall_row_start_time = pygame.time.get_ticks()
                self.pending_fall_rows = True

        # 处理行下落延迟
        if self.pending_fall_rows:
            current_time = pygame.time.get_ticks()
            if current_time - self.fall_row_start_time >= 3000:
                self.pending_fall_rows = False
                # 遍历所有行（从下往上），让能下落的行下落到底部
                moved = True
                while moved:
                    moved = False
                    for row in range(GRID_HEIGHT - 1, 0, -1):
                        for col in range(GRID_WIDTH):
                            if self.board[row][col] == 0 and self.board[row - 1][col] != 0:
                                # 下落
                                self.board[row][col] = self.board[row - 1][col]
                                self.board[row - 1][col] = 0
                                moved = True

        # 更新渐变动画
        for block in self.vanishing_blocks[:]:
            block['alpha'] = max(0, block['alpha'] - 25)
            if block['alpha'] == 0:
                self.vanishing_blocks.remove(block)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    game = Tetris()
    game.new_shape()

    while not game.game_over:
        game.update_fall_time()
        game.update_animation()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.game_over = True
            if event.type == pygame.KEYDOWN:
                if game.is_clearing or game.is_new_shape_delayed:
                    continue
                if event.key == pygame.K_LEFT:
                    game.move_left()
                if event.key == pygame.K_RIGHT:
                    game.move_right()
                if event.key == pygame.K_DOWN:
                    game.move_down()
                if event.key == pygame.K_UP:
                    game.rotate()

        game.check_game_over()
        game.increase_level()
        game.draw(screen)
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()