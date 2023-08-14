from pathlib import Path
import json

class GameStats:
    """跟踪游戏的统计信息"""

    def __init__(self, ai_game):
        """初始化统计信息"""
        self.settings = ai_game.settings
        self.reset_stats()

        # 在任何情况下都不应重置最高分
        self.remain_highest()

    def remain_highest(self):
        """记住不同难度的最高分"""
        path = Path(f'highest_score_{self.settings.difficulty_level}.json')
        if path.exists():
            contents = path.read_text()
            self.high_score = json.loads(contents)
        else:
            self.high_score = 0

    def reset_stats(self):
        """初始化在游戏运行期间可能发生变化的统计信息"""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1