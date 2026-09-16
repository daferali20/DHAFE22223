"""
==========================================
style.py - ملف التصميم الحي (Premium Fintech Theme)
تصميم عصري مستوحى من منصات التداول العالمية
==========================================
"""
import tkinter as tk
from tkinter import ttk

# ==========================================
# نظام الألوان (Premium Fintech Dark)
# ==========================================
class Colors:
    # الخلفيات (Deep Navy / Slate)
    BG_MAIN = '#0B1121'          # خلفية رئيسية (أزرق داكن جداً)
    BG_PANEL = '#111827'         # خلفية اللوحات الأساسية
    BG_TABLE = '#141E30'         # خلفية الجدول
    BG_TABLE_ALT = '#19253A'     # خلفية الصفوف المتناوبة (أفتح قليلاً)
    BG_HEADER = '#1F2937'        # خلفية الرؤوس (Slate)
    BG_CARD = '#151E2D'          # خلفية البطاقات الإحصائية
    
    # النصوص
    TEXT_PRIMARY = '#F3F4F6'     # أبيض ساطع للنصوص المهمة
    TEXT_SECONDARY = '#9CA3AF'   # رمادي مزرق للنصوص الثانوية
    TEXT_ACCENT = '#38BDF8'      # أزرق سماوي للتمييز
    TEXT_MUTED = '#4B5563'       # رمادي باهت
    
    # ألوان الأزرار (ألوان حيوية - Vibrant)
    PRIMARY = '#10B981'          # أخضر زمردي (زر الفحص)
    PRIMARY_HOVER = '#34D399'
    PRIMARY_DARK = '#047857'
    
    SECONDARY = '#6366F1'        # نيلي/بنفسجي (زر الحفظ)
    SECONDARY_HOVER = '#818CF8'
    SECONDARY_DARK = '#4338CA'
    
    DANGER = '#EF4444'           # أحمر ساطع
    DANGER_HOVER = '#F87171'
    
    # ألوان الفئات (باستيل/نيون لتباين ممتاز)
    TREASURE = '#10B981'         # Emerald Green
    GEM = '#F59E0B'              # Amber Gold
    DIAMOND = '#0EA5E9'          # Ocean Blue
    WATCH = '#F97316'            # Warm Orange
    REJECTED = '#64748B'         # Slate Gray
    
    # التدرجات (Gradients)
    TREASURE_GRAD = ('#10B981', '#059669')
    GEM_GRAD = ('#F59E0B', '#D97706')
    DIAMOND_GRAD = ('#0EA5E9', '#0284C7')
    WATCH_GRAD = ('#F97316', '#EA580C')
    
    # الحدود
    BORDER = '#374151'
    BORDER_LIGHT = '#1F2937'
    BORDER_GLOW = '#38BDF8'      # توهج أزرق سماوي
    
    # الظلال
    SHADOW_DARK = '#000000'
    SHADOW_LIGHT = '#0F172A'

# ==========================================
# إعدادات الخطوط
# ==========================================
class Fonts:
    # يفضل استخدام خطوط مثل Tajawal أو Cairo إذا كانت متوفرة بالنظام
    FAMILY = 'Tajawal' # يمكنك تغييره إلى 'Segoe UI' إذا لم يتوفر تجوال
    FAMILY_ARABIC = 'Tajawal'
    FAMILY_EMOJI = 'Segoe UI Emoji'
    
    SIZE_SMALL = 10
    SIZE_NORMAL = 11      # تم تكبير الخط الأساسي قليلاً للقراءة
    SIZE_MEDIUM = 12
    SIZE_LARGE = 14
    SIZE_TITLE = 20
    SIZE_HUGE = 26

# ==========================================
# إعداد أنماط ttk
# ==========================================
def setup_ttk_styles():
    style = ttk.Style()
    style.theme_use('clam')
    
    # شريط التقدم (أكثر نعومة)
    style.configure(
        'Modern.Horizontal.TProgressbar',
        background=Colors.PRIMARY,
        troughcolor=Colors.BG_MAIN,
        bordercolor=Colors.BG_MAIN,
        lightcolor=Colors.PRIMARY_HOVER,
        darkcolor=Colors.PRIMARY_DARK,
        thickness=12
    )
    
    # التبويبات (Tabs) - تصميم عصري بخطوط سفلية
    style.configure(
        'Modern.TNotebook',
        background=Colors.BG_MAIN,
        borderwidth=0
    )
    style.configure(
        'Modern.TNotebook.Tab',
        background=Colors.BG_MAIN,
        foreground=Colors.TEXT_SECONDARY,
        padding=[25, 15],
        font=(Fonts.FAMILY, Fonts.SIZE_MEDIUM),
        borderwidth=0,
        focuscolor=Colors.BG_MAIN
    )
    style.map(
        'Modern.TNotebook.Tab',
        background=[('selected', Colors.BG_PANEL), ('active', Colors.BG_CARD)],
        foreground=[('selected', Colors.TEXT_ACCENT), ('active', Colors.TEXT_PRIMARY)],
        expand=[('selected', [0, 0, 0, 0])] # منع تحرك التبويب عند التحديد
    )
    
    # الجداول (Table/Treeview) - مساحات أوسع وألوان أريح للعين
    for tier_key in ['treasure', 'gem', 'diamond', 'watch']:
        style.configure(
            f'{tier_key}.Treeview',
            background=Colors.BG_TABLE,
            foreground=Colors.TEXT_PRIMARY,
            fieldbackground=Colors.BG_TABLE,
            rowheight=42, # زيادة ارتفاع الصف لراحة العين
            font=(Fonts.FAMILY, Fonts.SIZE_NORMAL),
            borderwidth=0
        )
        style.configure(
            f'{tier_key}.Treeview.Heading',
            background=Colors.BG_HEADER,
            foreground=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SIZE_NORMAL, 'bold'),
            padding=[5, 10],
            borderwidth=0,
            relief='flat'
        )
        # لون التحديد عند اختيار سهم معين
        style.map(
            f'{tier_key}.Treeview',
            background=[('selected', '#2563EB')], # أزرق تفاعلي للتحديد
            foreground=[('selected', '#FFFFFF')]
        )
        style.map(
            f'{tier_key}.Treeview.Heading',
            background=[('active', Colors.BG_CARD)]
        )

# ==========================================
# زر بتصميم متدرج (Gradient Button) - مُحسّن
# ==========================================
class GradientButton(tk.Canvas):
    def __init__(self, parent, text, gradient_colors, command,
                 width=200, height=45, font_size=12, state='normal'):
        super().__init__(
            parent, width=width, height=height,
            bg=Colors.BG_PANEL, highlightthickness=0, bd=0
        )
        
        self.text = text
        self.command = command
        self.width = width
        self.height = height
        self.colors = gradient_colors
        self.state = state
        self.font_size = font_size
        
        self.draw_button(self.colors)
        
        if state == 'normal':
            self.bind('<Enter>', self.on_enter)
            self.bind('<Leave>', self.on_leave)
            self.bind('<Button-1>', self.on_click)
            self.configure(cursor='hand2')
    
    def draw_button(self, colors):
        self.delete('all')
        c1, c2 = colors
        
        # التدرج اللوني (أكثر نعومة)
        for i in range(self.height):
            ratio = i / self.height
            r1, g1, b1 = self._hex_to_rgb(c1)
            r2, g2, b2 = self._hex_to_rgb(c2)
            
            r = int(r1 * (1 - ratio) + r2 * ratio)
            g = int(g1 * (1 - ratio) + g2 * ratio)
            b = int(b1 * (1 - ratio) + b2 * ratio)
            
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.create_line(0, i, self.width, i, fill=color)
        
        # إطار داخلي شفاف لإعطاء بروز 3D خفيف
        self.create_rectangle(
            1, 1, self.width - 1, self.height - 1,
            outline='#FFFFFF', width=1, stipple='gray12'
        )
        
        # النص مع ظل خفيف
        self.create_text(
            self.width / 2, (self.height / 2) + 1,
            text=self.text,
            font=(Fonts.FAMILY, self.font_size, 'bold'),
            fill=Colors.SHADOW_DARK
        )
        self.create_text(
            self.width / 2, self.height / 2,
            text=self.text,
            font=(Fonts.FAMILY, self.font_size, 'bold'),
            fill='white'
        )
    
    def on_enter(self, event):
        lighter = tuple(self._lighten(c, 0.15) for c in self.colors)
        self.draw_button(lighter)
    
    def on_leave(self, event):
        self.draw_button(self.colors)
    
    def on_click(self, event):
        self.move('all', 0, 2)
        self.after(100, lambda: self.move('all', 0, -2))
        if self.command:
            self.command()
    
    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _lighten(self, hex_color, amount):
        r, g, b = self._hex_to_rgb(hex_color)
        r = min(255, int(r + (255 - r) * amount))
        g = min(255, int(g + (255 - g) * amount))
        b = min(255, int(b + (255 - b) * amount))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def config_state(self, state):
        self.state = state
        if state == 'disabled':
            self.unbind('<Enter>')
            self.unbind('<Leave>')
            self.unbind('<Button-1>')
            self.configure(cursor='arrow')
            self.delete('all')
            for i in range(self.height):
                self.create_line(0, i, self.width, i, fill=Colors.BG_CARD)
            self.create_text(
                self.width / 2, self.height / 2,
                text=self.text,
                font=(Fonts.FAMILY, self.font_size, 'bold'),
                fill=Colors.TEXT_MUTED
            )
        else:
            self.draw_button(self.colors)
            self.bind('<Enter>', self.on_enter)
            self.bind('<Leave>', self.on_leave)
            self.bind('<Button-1>', self.on_click)
            self.configure(cursor='hand2')

# ==========================================
# بطاقة إحصائية حية - مُحسّنة
# ==========================================
class StatCard(tk.Frame):
    def __init__(self, parent, emoji, name, color, gradient=None):
        super().__init__(parent, bg=Colors.BG_CARD, padx=16, pady=12) # زيادة الـ Padding
        
        self.color = color
        self.gradient = gradient or (color, color)
        self.current_value = 0
        self.animation_running = False
        
        # شريط جانبي أسمك يعطي هوية بصرية قوية
        self.accent = tk.Frame(self, bg=color, width=6)
        self.accent.pack(side='right', fill='y', padx=(12, 0)) # تم النقل لليمين لدعم اللغة العربية
        
        # الإيموجي
        self.emoji_label = tk.Label(
            self, text=emoji,
            font=(Fonts.FAMILY_EMOJI, 22), # تكبير الإيموجي
            bg=Colors.BG_CARD, fg=color
        )
        self.emoji_label.pack(side='right', padx=(0, 10))
        
        # الإطار النصي
        text_frame = tk.Frame(self, bg=Colors.BG_CARD)
        text_frame.pack(side='right', padx=(10, 0))
        
        # الاسم (تم وضعه فوق العدد ليكون أكثر ترتيباً)
        self.name_label = tk.Label(
            text_frame, text=name,
            font=(Fonts.FAMILY, Fonts.SIZE_MEDIUM),
            bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY
        )
        self.name_label.pack(anchor='e')
        
        # العدد
        self.count_label = tk.Label(
            text_frame, text="0",
            font=(Fonts.FAMILY, Fonts.SIZE_HUGE, 'bold'),
            bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY
        )
        self.count_label.pack(anchor='e')
        
        # تأثير Hover
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        for child in [self.emoji_label, self.count_label, self.name_label, text_frame]:
            child.bind('<Enter>', self.on_enter)
            child.bind('<Leave>', self.on_leave)
            child.configure(cursor='hand2')
    
    def on_enter(self, event):
        self.configure(bg=Colors.BG_HEADER)
        self.emoji_label.configure(bg=Colors.BG_HEADER)
        self.count_label.configure(bg=Colors.BG_HEADER, fg=self.color)
        self.name_label.configure(bg=Colors.BG_HEADER, fg=Colors.TEXT_PRIMARY)
        for child in self.winfo_children():
            if isinstance(child, tk.Frame) and child != self.accent:
                child.configure(bg=Colors.BG_HEADER)
                for sub in child.winfo_children():
                    if isinstance(sub, tk.Label) and sub != self.count_label:
                        sub.configure(bg=Colors.BG_HEADER)
    
    def on_leave(self, event):
        self.configure(bg=Colors.BG_CARD)
        self.emoji_label.configure(bg=Colors.BG_CARD)
        self.count_label.configure(bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY)
        self.name_label.configure(bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY)
        for child in self.winfo_children():
            if isinstance(child, tk.Frame) and child != self.accent:
                child.configure(bg=Colors.BG_CARD)
                for sub in child.winfo_children():
                    if isinstance(sub, tk.Label):
                        sub.configure(bg=Colors.BG_CARD)
    
    def set_value(self, new_value):
        if new_value == self.current_value or self.animation_running:
            return
            
        self.animation_running = True
        start = self.current_value
        end = new_value
        steps = 20 # زيادة نعومة الحركة
        
        def animate(step):
            if step > steps:
                self.current_value = end
                self.count_label.config(text=str(end))
                self.animation_running = False
                return
            
            progress = step / steps
            eased = 1 - (1 - progress) ** 3
            current = int(start + (end - start) * eased)
            self.count_label.config(text=str(current))
            self.after(15, lambda: animate(step + 1))
        
        animate(0)

# ==========================================
# دوال مساعدة
# ==========================================
def create_gradient_button(parent, text, colors, command,
                           width=200, height=45, font_size=12, state='normal'):
    return GradientButton(
        parent, text, colors, command,
        width=width, height=height,
        font_size=font_size, state=state
    )

def create_stat_card(parent, emoji, name, color, gradient=None):
    return StatCard(parent, emoji, name, color, gradient)

def create_section_divider(parent):
    canvas = tk.Canvas(
        parent, height=2, # فاصل أكثر وضوحاً
        bg=Colors.BG_MAIN, highlightthickness=0, bd=0
    )
    canvas.pack(fill='x', padx=30, pady=15)
    
    def draw(event=None):
        canvas.delete('all')
        w = canvas.winfo_width()
        if w > 1:
            for i in range(w):
                ratio = i / w
                intensity = 1 - abs(ratio - 0.5) * 2
                intensity = intensity ** 2
                
                r = int(0x38 * intensity + 0x0B * (1 - intensity))
                g = int(0xBD * intensity + 0x11 * (1 - intensity))
                b = int(0xF8 * intensity + 0x21 * (1 - intensity))
                
                color = f'#{r:02x}{g:02x}{b:02x}'
                canvas.create_line(i, 0, i, 2, fill=color)
    
    canvas.bind('<Configure>', draw)
    return canvas

def pulse_widget(widget, color1, color2, duration=1000):
    def pulse(step=0):
        total_steps = 20
        half = total_steps // 2
        
        ratio = step / half if step <= half else (total_steps - step) / half
        
        c1 = widget._hex_to_rgb(color1) if hasattr(widget, '_hex_to_rgb') else (16,185,129)
        c2 = widget._hex_to_rgb(color2) if hasattr(widget, '_hex_to_rgb') else (255,255,255)
        
        r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
        g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
        b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
        color = f'#{r:02x}{g:02x}{b:02x}'
        
        try:
            widget.configure(fg=color)
        except:
            pass
        
        if step < total_steps:
            widget.after(duration // total_steps, lambda: pulse(step + 1))
    
    pulse()

def animate_row_insert(tree, item_id):
    tree.item(item_id, tags=('new_row',))
    tree.tag_configure('new_row', background='#064E3B') # أخضر داكن للإضافة
    
    def restore():
        try:
            tree.item(item_id, tags=('even',))
        except:
            pass
    
    tree.after(800, restore)

# ==========================================
# قاموس ألوان الفئات
# ==========================================
TIER_COLORS = {
    'treasure': Colors.TREASURE,
    'gem': Colors.GEM,
    'diamond': Colors.DIAMOND,
    'watch': Colors.WATCH,
    'rejected': Colors.REJECTED,
}

TIER_GRADIENTS = {
    'treasure': Colors.TREASURE_GRAD,
    'gem': Colors.GEM_GRAD,
    'diamond': Colors.DIAMOND_GRAD,
    'watch': Colors.WATCH_GRAD,
    'rejected': (Colors.REJECTED, Colors.REJECTED),
}

TIER_EMOJIS = {
    'treasure': '💎',
    'gem': '🌟',
    'diamond': '💠',
    'watch': '⚠️',
    'rejected': '❌',
}

TIER_NAMES = {
    'treasure': 'كنوز',
    'gem': 'جواهر',
    'diamond': 'ماس خام',
    'watch': 'مراقبة',
    'rejected': 'مستبعد',
}