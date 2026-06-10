import pygame
import random

# 游戏参数
SCREEN_WIDTH = 240  # 游戏窗口宽度
SCREEN_HEIGHT = 240  # 游戏窗口高度
BLOCK_SIZE = 30  # 每个方块的尺寸
GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE  # 网格宽度（8列）
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE  # 网格高度（8行）
FPS = 10  # 设置帧率

# 定义颜色
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

# 定义俄罗斯方块形状及其颜色
SHAPES = [
    [[1, 1, 1, 1]],  # I形
    [[1, 1, 0], [0, 1, 1]],  # Z形
    [[0, 1, 1], [1, 1, 0]],  # S形
    [[1, 1], [1, 1]],  # O形
    [[1, 1, 1], [0, 1, 0]],  # T形
    [[0, 0, 1], [1, 1, 1]],  # L形
    [[1, 0, 0], [1, 1, 1]],  # J形
]

# 为每种形状指定一个颜色
SHAPE_COLORS = [
    (255, 255, 151),  # I形 (修改为 R:255, G:255, B:151)
    (117, 117, 209),  # Z形 (修改为 R:117, G:117, B:209)
    (87, 211, 255),  # S形 (修改为 R:87, G:211, B:255)
    (178, 222, 30),  # O形 (修改为 R:178, G:222, B:30)
    (158, 211, 215),  # T形 (修改为 R:158, G:211, B:215)
    (255, 79, 79),  # L形 (修改为 R:255, G:79, B:79)
    (255, 205, 47),  # J形 (修改为 R:255, G:205, B:47)
]

# 游戏主类
class Tetris:
    def __init__(self):
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]  # 初始化空的游戏面板
        self.game_over = False
        self.current_shape = None
        self.current_color = None
        self.x = 0
        self.y = 0
        self.shape_counter = 0  # 用于记录方块顺序
        self.fall_time = 0  # 控制降落的时间
        self.speed = 1000  # 方块下落速度（毫秒）
        self.move_speed = 1  # 平移的格子数
        self.last_move_time = 0  # 上次平移的时间
        self.move_delay = 200  # 平移按键延迟时间（毫秒）

    def new_shape(self):
        # 修改方块生成顺序，按照 I → O → J → Z → S → L → T 的顺序
        shape_order = [4, 2, 0, 6, 2, 5, 4]  # I, O, J, Z, S, L, T
        shape_index = shape_order[self.shape_counter % len(shape_order)]

        self.current_shape = SHAPES[shape_index]
        self.current_color = SHAPE_COLORS[shape_index]
        self.x = GRID_WIDTH // 2 - len(self.current_shape[0]) // 2  # 方块水平居中
        self.y = 0  # 方块从顶部开始

        # 更新方块顺序
        self.shape_counter += 1

    def collide(self):
        for i, row in enumerate(self.current_shape):
            for j, cell in enumerate(row):
                if cell:
                    if (self.x + j < 0 or self.x + j >= len(self.board[0]) or
                            self.y + i >= len(self.board) or self.board[self.y + i][self.x + j]):
                        return True
        return False

    def freeze(self):
        for i, row in enumerate(self.current_shape):
            for j, cell in enumerate(row):
                if cell:
                    self.board[self.y + i][self.x + j] = self.current_color
        self.clear_lines()
        self.new_shape()

    def clear_lines(self):
        full_lines = []
        for i, row in enumerate(self.board):
            if all(cell != 0 for cell in row):
                full_lines.append(i)
        for line in full_lines:
            self.board.pop(line)
            self.board.insert(0, [0 for _ in range(len(self.board[0]))])

    def rotate(self):
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

    def move_left(self):
        if self.valid_position():
            self.x -= self.move_speed
            if self.collide():
                self.x += self.move_speed

    def move_right(self):
        if self.valid_position():
            self.x += self.move_speed
            if self.collide():
                self.x -= self.move_speed

    def move_down(self):
        self.y += 1
        if self.collide():
            self.y -= 1
            self.freeze()

    def draw(self, screen):
        screen.fill(BLACK)  # 背景改成黑色
        # 绘制网格线（灰色）
        for i in range(GRID_HEIGHT):
            pygame.draw.line(screen, (169, 169, 169), (0, i * BLOCK_SIZE), (SCREEN_WIDTH, i * BLOCK_SIZE))  # 横线
        for i in range(GRID_WIDTH):
            pygame.draw.line(screen, (169, 169, 169), (i * BLOCK_SIZE, 0), (i * BLOCK_SIZE, SCREEN_HEIGHT))  # 竖线
        # 绘制已固定的方块
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j]:
                    pygame.draw.rect(screen, self.board[i][j], (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        # 绘制当前形状
        for i, row in enumerate(self.current_shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, self.current_color,
                                     ((self.x + j) * BLOCK_SIZE, (self.y + i) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        # 如果游戏结束，显示 GAME OVER
        if self.game_over:
            font = pygame.font.SysFont(None, 50)
            game_over_text = font.render("GAME OVER", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))

        pygame.display.update()

    def update(self):
        self.fall_time += 1
        if self.fall_time % self.speed == 0:
            self.move_down()

# 游戏主循环
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)  # 去掉边框和透明
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()

    game = Tetris()
    game.new_shape()

    while not game.game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move_left()
                if event.key == pygame.K_RIGHT:
                    game.move_right()
                if event.key == pygame.K_DOWN:
                    game.move_down()
                if event.key == pygame.K_UP:
                    game.rotate()

        game.update()
        game.draw(screen)
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
