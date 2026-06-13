import os

BASE = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(BASE, "app", "main.py")

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# tabs = QTabWidget() -> self.tabs = QTabWidget()
content = content.replace('tabs = QTabWidget()', 'self.tabs = QTabWidget()')

# main_layout.addWidget(tabs) -> main_layout.addWidget(self.tabs)
content = content.replace('main_layout.addWidget(tabs)', 'main_layout.addWidget(self.tabs)')

# tabs.addTab -> self.tabs.addTab
content = content.replace('tabs.addTab(', 'self.tabs.addTab(')

# _retranslate_ui içindeki tabs.findChild -> self.tabs
content = content.replace('tabs = self.findChild(QTabWidget)', '# tabs zaten self.tabs')

# Kaydet
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ tabs -> self.tabs dönüşümü tamamlandı.")