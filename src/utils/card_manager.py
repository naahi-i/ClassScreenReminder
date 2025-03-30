class CardManager:
    """名片管理器，负责名片的保存和加载"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.cards = self._load_cards()
    
    def _load_cards(self):
        """从配置中加载名片数据"""
        return self.config_manager.get_setting("cards", [])
    
    def save_cards(self):
        """保存名片数据到配置"""
        self.config_manager.set_setting("cards", self.cards)
    
    def add_card(self, card_data):
        """添加新名片"""
        self.cards.append(card_data)
        self.save_cards()
    
    def delete_card(self, index):
        """删除名片"""
        if 0 <= index < len(self.cards):
            del self.cards[index]
            self.save_cards()
            return True
        return False
    
    def get_all_cards(self):
        """获取所有名片"""
        return self.cards.copy()
