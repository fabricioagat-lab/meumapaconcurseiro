from kivy.lang import Builder
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty
from kivy.clock import Clock
import json, os
from datetime import datetime
try:
    from plyer import notification
except Exception:
    notification = None

Window.clearcolor = (0.07, 0.14, 0.28, 1)  # azul marinho

KV = '''
ScreenManager:
    MenuScreen:
    MapEditorScreen:
    MyMapsScreen:

<MenuScreen>:
    name: 'menu'
    BoxLayout:
        orientation: 'vertical'
        padding: 12
        spacing: 12
        Label:
            text: 'Meu Mapa Concurseiro'
            font_size: '28sp'
            size_hint_y: None
            height: '48dp'
        Button:
            text: 'Criar novo mapa'
            on_release: app.open_new_map()
        Button:
            text: 'Meus mapas'
            on_release: app.root.current = 'mymaps'
        Button:
            text: 'Exportar último mapa (PDF)'
            on_release: app.export_last_map()

<MapEditorScreen>:
    name: 'editor'
    BoxLayout:
        orientation: 'vertical'
        padding: 8
        spacing: 8
        TextInput:
            id: title
            hint_text: 'Título do mapa'
            size_hint_y: None
            height: '40dp'
        TextInput:
            id: content
            hint_text: 'Tópicos separados por vírgula (Tema, Subtema, Definição)'
        BoxLayout:
            size_hint_y: None
            height: '48dp'
            spacing: 8
            Button:
                text: 'Salvar mapa'
                on_release: app.save_map(title.text, content.text)
            Button:
                text: 'Voltar'
                on_release: app.root.current = 'menu'

<MyMapsScreen>:
    name: 'mymaps'
    BoxLayout:
        orientation: 'vertical'
        padding: 8
        spacing: 8
        ScrollView:
            GridLayout:
                id: maps_grid
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                row_default_height: '64dp'
        BoxLayout:
            size_hint_y: None
            height: '48dp'
            Button:
                text: 'Voltar'
                on_release: app.root.current = 'menu'
'''

class MenuScreen(Screen): pass
class MapEditorScreen(Screen): pass
class MyMapsScreen(Screen): pass

class MyApp(App):
    data_file = 'app_data/maps.json'
    maps = ListProperty([])

    def build(self):
        if not os.path.exists('app_data'):
            os.makedirs('app_data')
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
        self.load_maps()
        self.sm = Builder.load_string(KV)
        Clock.schedule_once(lambda dt: self.populate_maps(), 0.5)
        return self.sm

    def load_maps(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.maps = json.load(f)
        except Exception:
            self.maps = []

    def save_maps(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.maps, f, ensure_ascii=False, indent=2)

    def open_new_map(self):
        self.root.current = 'editor'

    def save_map(self, title, content):
        if not title:
            title = f'Mapa {len(self.maps)+1} - ' + datetime.now().strftime('%Y-%m-%d %H:%M')
        topics = [t.strip() for t in content.split(',') if t.strip()]
        m = {'title': title, 'topics': topics, 'created_at': datetime.now().isoformat()}
        self.maps.insert(0, m)
        self.save_maps()
        self.notify('Mapa salvo', title)
        self.root.current = 'menu'
        self.populate_maps()

    def populate_maps(self):
        try:
            grid = self.root.get_screen('mymaps').ids.maps_grid
        except Exception:
            return
        grid.clear_widgets()
        from kivy.uix.button import Button
        for i, m in enumerate(self.maps):
            b = Button(text=f"{m['title']} - {len(m['topics'])} tópicos",
                       size_hint_y=None, height='64dp')
            b.bind(on_release=lambda btn, idx=i: self.open_map(idx))
            grid.add_widget(b)

    def open_map(self, idx):
        m = self.maps[idx]
        ed = self.root.get_screen('editor')
        ed.ids.title.text = m['title']
        ed.ids.content.text = ', '.join(m['topics'])
        self.root.current = 'editor'

    def export_last_map(self):
        if len(self.maps) == 0:
            self.notify('Erro', 'Nenhum mapa salvo')
            return
        m = self.maps[0]
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            fn = f"/sdcard/{m['title'].replace(' ','_')}.pdf"
            c = canvas.Canvas(fn, pagesize=A4)
            c.setFont('Helvetica-Bold', 18)
            c.drawString(40, 800, m['title'])
            c.setFont('Helvetica', 12)
            y = 770
            for t in m['topics']:
                c.drawString(50, y, '- ' + t)
                y -= 20
            c.save()
            self.notify('Exportado', f'PDF salvo em {fn}')
        except Exception as e:
            self.notify('Export falhou', str(e))

    def notify(self, title, msg):
        try:
            if notification:
                notification.notify(title=title, message=msg)
        except Exception:
            pass

if __name__ == '__main__':
    MyApp().run()
