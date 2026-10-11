from .theme import LIGHT, DARK


def build_qss(c: dict) -> str:
    return f"""
    QMainWindow, QWidget {{
        background-color: {c['bg']};
        color: {c['text']};
        font-family: "Segoe UI", "Inter", "Helvetica Neue", sans-serif;
        font-size: 13px;
    }}

    QLabel {{
        background: transparent;
        color: {c['text']};
    }}

    #Sidebar {{
        background-color: {c['sidebar']};
        border-right: 1px solid {c['border']};
    }}

    #SidebarTitle {{
        color: {c['accent']};
        font-size: 15px;
        font-weight: 700;
        padding: 18px 16px 6px 16px;
        letter-spacing: 1px;
        background: transparent;
    }}

    #SidebarSep {{
        background-color: {c['border']};
        max-height: 1px;
        margin: 6px 14px;
        border: none;
    }}
    QToolButton#ToolButton {{
        background-color: transparent;
        border: none;
        border-radius: 9px;
        color: {c['text_dim']};
        padding: 10px;
        margin: 3px 10px;
        font-size: 18px;
        text-align: center;
    }}

    QToolButton#ToolButton:hover {{
        background-color: {c['accent_lo']};
        color: {c['text']};
    }}

    QToolButton#ToolButton:checked {{
        background-color: {c['accent']};
        color: #FFFFFF;
    }}

    #Workspace {{
        background-color: {c['bg']};
    }}

    #WorkspaceCard {{
        background-color: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 14px;
    }}

    #WorkspaceCard QLabel,
    #WorkspaceCard QToolButton {{
        background: transparent;
    }}

    #WorkspaceTitle {{
        font-size: 22px;
        font-weight: 600;
        color: {c['text']};
        background: transparent;
    }}

    #WorkspaceHint {{
        font-size: 13px;
        color: {c['text_dim']};
        background: transparent;
    }}

    #WorkspaceSubtitle {{
        font-size: 12px;
        color: {c['text_mute']};
        background: transparent;
    }}

    #SettingsLabel {{
        font-size: 13px;
        color: {c['text']};
        font-weight: 500;
        background: transparent;
    }}

    #SettingsHint {{
        font-size: 12px;
        color: {c['text_dim']};
        background: transparent;
    }}

    QToolButton#ThemeArrow {{
        background-color: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 15px;
        color: {c['accent']};
        font-size: 16px;
        font-weight: 700;
    }}

    QToolButton#ThemeArrow:hover {{
        background-color: {c['accent_lo']};
        border-color: {c['accent_hi']};
    }}

    QToolButton#ThemeArrow:pressed {{
        background-color: {c['accent']};
        color: #FFFFFF;
    }}

    QLabel#ThemeValue {{
        color: {c['text']};
        font-size: 13px;
        font-weight: 500;
        padding: 6px 4px;
        background: transparent;
    }}

    QToolTip {{
        background-color: {c['tooltip_bg']};
        color: {c['tooltip_fg']};
        border: none;
        border-radius: 6px;
        padding: 8px 10px;
        font-size: 12px;
    }}

    QStatusBar {{
        background-color: {c['sidebar']};
        color: {c['text_dim']};
        border-top: 1px solid {c['border']};
    }}

    QStatusBar QLabel {{
        background: transparent;
        color: {c['text_dim']};
    }}
    #TitleBar {{
        background-color: {c['sidebar']};
        border-bottom: 1px solid {c['border']};
    }}

    #TitleLogo {{
        background-color: {c['accent']};
        color: #FFFFFF;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
    }}

    #TitleText {{
        color: {c['text']};
        font-size: 13px;
        font-weight: 500;
        background: transparent;
    }}

    QToolButton#WinBtnMin,
    QToolButton#WinBtnMax,
    QToolButton#WinBtnClose {{
        background: transparent;
        border: none;
        border-radius: 6px;
        color: {c['text_dim']};
        font-size: 13px;
        font-weight: 600;
    }}

    QToolButton#WinBtnMin:hover,
    QToolButton#WinBtnMax:hover {{
        background-color: {c['accent_lo']};
        color: {c['text']};
    }}

    QToolButton#WinBtnClose:hover {{
        background-color: {c['danger']};
        color: #FFFFFF;
    }}
    QLineEdit#SearchInput {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        padding: 10px 14px;
        color: {c['text']};
        font-size: 13px;
        selection-background-color: {c['accent']};
        selection-color: #FFFFFF;
    }}

    QLineEdit#SearchInput:focus {{
        border-color: {c['accent']};
        background-color: {c['card']};
    }}

    #ToolCard {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 10px;
    }}

    #ToolCard:hover {{
        background-color: {c['accent_lo']};
        border-color: {c['accent_hi']};
    }}

    #ToolCardName {{
        font-size: 13px;
        font-weight: 600;
        color: {c['text']};
        background: transparent;
    }}

    #ToolCardDesc {{
        font-size: 12px;
        color: {c['text_dim']};
        background: transparent;
    }}

    #ToolCardGroup {{
        font-size: 11px;
        color: {c['text_mute']};
        background: transparent;
        padding-right: 4px;
    }}

    #SearchEmpty {{
        font-size: 13px;
        color: {c['text_dim']};
        padding: 40px 0;
        background: transparent;
    }}

    QScrollArea#SearchScroll {{
        background: transparent;
        border: none;
    }}

    QScrollArea#SearchScroll > QWidget > QWidget {{
        background: transparent;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background: {c['border_hi']};
        border-radius: 4px;
        min-height: 24px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {c['accent_hi']};
    }}

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        background: none;
        border: none;
        height: 0;
    }}
    QFrame#SettingsSep {{
        background-color: {c['border']};
        border: none;
        max-height: 1px;
    }}

    QToolButton#LinkBtnGitHub,
    QToolButton#LinkBtnTelegram {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        color: {c['text']};
        font-size: 13px;
        font-weight: 500;
        padding: 6px 16px;
    }}

    QToolButton#LinkBtnGitHub:hover {{
        background-color: {c['accent_lo']};
        border-color: {c['accent_hi']};
        color: {c['accent']};
    }}

    QToolButton#LinkBtnTelegram:hover {{
        background-color: {c['accent_lo']};
        border-color: {c['accent_hi']};
        color: {c['accent']};
    }}

    QToolButton#LinkBtnGitHub:pressed,
    QToolButton#LinkBtnTelegram:pressed {{
        background-color: {c['accent']};
        color: #FFFFFF;
    }}
    #SettingsSection {{
        font-size: 12px;
        font-weight: 700;
        color: {c['text_mute']};
        text-transform: uppercase;
        letter-spacing: 0.8px;
        background: transparent;
        padding: 4px 0 0 0;
    }}

    QScrollArea#SettingsScroll {{
        background: transparent;
        border: none;
    }}

    QScrollArea#SettingsScroll > QWidget > QWidget {{
        background: transparent;
    }}

    QToolButton#ToggleSwitch {{
        background-color: {c['border']};
        border: none;
        border-radius: 12px;
    }}

    QToolButton#ToggleSwitch:checked {{
        background-color: {c['success']};
    }}

    QToolButton#ToggleSwitch::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 9px;
        background: #FFFFFF;
        margin: 3px;
    }}

    QToolButton#ToggleSwitch:checked::indicator {{
        margin-left: 23px;
    }}
    QLineEdit#PathInput {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 6px 10px;
        color: {c['text']};
        font-size: 12px;
    }}

    QWidget#RadioHost,
    QWidget#SettingControlHost,
    QWidget#SettingsHeader,
    QWidget#SettingsBody,
    QScrollArea#SettingsScroll,
    QScrollArea#SettingsScroll > QWidget > QWidget {{
        background: transparent;
        border: none;
    }}

    QRadioButton {{
        background: transparent;
        color: {c['text']};
        font-size: 13px;
        padding: 4px 2px;
        spacing: 8px;
    }}

    QRadioButton#LangRadio {{
        background: transparent;
        color: {c['text']};
    }}

    QRadioButton#LangRadio::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 9px;
        border: 1.5px solid {c['border']};
        background: {c['card']};
    }}

    QRadioButton#LangRadio::indicator:checked {{
        border: 5px solid {c['accent']};
        background: {c['card']};
    }}

    QRadioButton#LangRadio::indicator:hover {{
        border-color: {c['accent_hi']};
    }}
    #HomeLogo {{
        background-color: {c['accent']};
        color: #FFFFFF;
        border-radius: 22px;
        font-family: "Segoe UI Semibold", "Inter", sans-serif;
        font-size: 32px;
        font-weight: 700;
        letter-spacing: 1px;
    }}

    #HomeTitle {{
        font-family: "Segoe UI Light", "Inter Light", sans-serif;
        font-size: 36px;
        font-weight: 300;
        color: {c['text']};
        letter-spacing: 1.5px;
        background: transparent;
    }}

    #HomeVersion {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 11px;
        font-weight: 500;
        color: {c['text_mute']};
        letter-spacing: 2.5px;
        background: transparent;
    }}

    #HomeDesc {{
        font-family: "Segoe UI", "Inter", sans-serif;
        font-size: 14px;
        font-weight: 400;
        color: {c['text_dim']};
        line-height: 1.6;
        background: transparent;
        padding: 0 40px;
    }}

    #HomeSection {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 11px;
        font-weight: 600;
        color: {c['text_mute']};
        letter-spacing: 3px;
        background: transparent;
    }}

    #HomeFeaturesHost {{
        background: transparent;
    }}

    #HomeFeatureCell {{
        background: transparent;
    }}

    #HomeFeatureBullet {{
        color: {c['accent']};
        font-size: 16px;
        font-weight: 700;
        background: transparent;
    }}

    #HomeFeature {{
        font-family: "Segoe UI", "Inter", sans-serif;
        font-size: 13px;
        font-weight: 400;
        color: {c['text']};
        background: transparent;
    }}

    #HomeHint {{
        font-family: "Segoe UI", "Inter", sans-serif;
        font-size: 12px;
        font-weight: 400;
        font-style: italic;
        color: {c['text_mute']};
        background: transparent;
    }}
    QWidget#InfoTopBar,
    QWidget#InfoDropHost,
    QWidget#InfoResultHost,
    QWidget#InfoGroup,
    QWidget#InfoGrid {{
        background: transparent;
    }}

    QToolButton#InfoBrowseBtn {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        color: {c['text']};
        padding: 6px 14px;
        font-size: 12px;
    }}

    QToolButton#InfoBrowseBtn:hover {{
        background-color: {c['accent_lo']};
        border-color: {c['accent_hi']};
        color: {c['accent']};
    }}

    QToolButton#InfoBrowseBtn:pressed {{
        background-color: {c['accent']};
        color: #FFFFFF;
    }}

    QFrame#DropZone {{
        background-color: {c['bg']};
        border: 2px dashed {c['border']};
        border-radius: 12px;
    }}

    QFrame#DropZone[hovered="true"] {{
        background-color: {c['accent_lo']};
        border-color: {c['accent']};
    }}

    QLabel#DropZoneIcon {{
        color: {c['accent']};
        font-size: 32px;
        background: transparent;
    }}

    QLabel#DropZoneText {{
        color: {c['text_dim']};
        font-size: 13px;
        background: transparent;
    }}

    QLabel#InfoGroupTitle {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 11px;
        font-weight: 700;
        color: {c['text_mute']};
        letter-spacing: 2px;
        background: transparent;
        padding-top: 6px;
    }}

    QLabel#InfoKey {{
        font-size: 12px;
        color: {c['text_mute']};
        background: transparent;
    }}

    QLabel#InfoValue {{
        font-size: 13px;
        color: {c['text']};
        background: transparent;
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
    }}

    QLabel#InfoEmpty {{
        font-size: 13px;
        color: {c['text_dim']};
        padding: 40px 0;
        background: transparent;
    }}

    QLabel#InfoError {{
        font-size: 13px;
        color: {c['danger']};
        padding: 30px 0;
        background: transparent;
    }}

    QScrollArea#InfoScroll,
    QScrollArea#InfoScroll > QWidget > QWidget {{
        background: transparent;
        border: none;
    }}
    QWidget#HashTopBar,
    QWidget#HashDropHost,
    QWidget#HashAlgosHost,
    QWidget#HashAlgosGrid,
    QWidget#HashProgressHost,
    QWidget#HashResultHost {{
        background: transparent;
    }}

    QLabel#HashSectionTitle {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 11px;
        font-weight: 700;
        color: {c['text_mute']};
        letter-spacing: 2px;
        background: transparent;
        padding-top: 6px;
    }}

    QCheckBox#HashCheckbox {{
        background: transparent;
        color: {c['text']};
        font-size: 13px;
        padding: 4px 2px;
        spacing: 8px;
    }}

    QCheckBox#HashCheckbox::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 4px;
        border: 1.5px solid {c['border']};
        background: {c['card']};
    }}

    QCheckBox#HashCheckbox::indicator:hover {{
        border-color: {c['accent_hi']};
    }}

    QCheckBox#HashCheckbox::indicator:checked {{
        background-color: {c['accent']};
        border-color: {c['accent']};
        image: none;
    }}

    QProgressBar#HashProgress {{
        background-color: {c['border']};
        border: none;
        border-radius: 3px;
        height: 6px;
    }}

    QProgressBar#HashProgress::chunk {{
        background-color: {c['accent']};
        border-radius: 3px;
    }}

    #HashRow {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 8px;
    }}

    QLabel#HashName {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 12px;
        font-weight: 700;
        color: {c['accent']};
        background: transparent;
    }}

    QLabel#HashValue {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 12px;
        color: {c['text']};
        background: transparent;
    }}

    QToolButton#HashCopyBtn {{
        background-color: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        color: {c['text_dim']};
        font-size: 14px;
        padding: 2px 8px;
    }}

    QToolButton#HashCopyBtn:hover {{
        background-color: {c['accent_lo']};
        border-color: {c['accent_hi']};
        color: {c['accent']};
    }}

    QToolButton#HashCopyBtn:disabled {{
        color: {c['text_mute']};
        border-color: {c['border']};
    }}

    QLabel#HashEmpty {{
        font-size: 13px;
        color: {c['text_dim']};
        padding: 40px 0;
        background: transparent;
    }}

    QLabel#HashError {{
        font-size: 13px;
        color: {c['danger']};
        padding: 30px 0;
        background: transparent;
    }}

    QScrollArea#HashScroll,
    QScrollArea#HashScroll > QWidget > QWidget {{
        background: transparent;
        border: none;
    }}
    QWidget#MetaTopBar,
    QWidget#MetaDropHost,
    QWidget#MetaResultHost,
    QWidget#MetaGroup,
    QWidget#MetaGrid {{
        background: transparent;
    }}

    QLabel#MetaGroupTitle {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 11px;
        font-weight: 700;
        color: {c['text_mute']};
        letter-spacing: 2px;
        background: transparent;
        padding-top: 6px;
    }}

    QLabel#MetaKey {{
        font-size: 12px;
        color: {c['text_mute']};
        background: transparent;
    }}

    QLabel#MetaValue {{
        font-size: 13px;
        color: {c['text']};
        background: transparent;
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
    }}

    QLabel#MetaEmpty {{
        font-size: 13px;
        color: {c['text_dim']};
        padding: 40px 0;
        background: transparent;
    }}

    QLabel#MetaError {{
        font-size: 13px;
        color: {c['danger']};
        padding: 30px 0;
        background: transparent;
    }}

    QScrollArea#MetaScroll,
    QScrollArea#MetaScroll > QWidget > QWidget {{
        background: transparent;
        border: none;
    }}
    QWidget#ConvertTopBar,
    QWidget#ConvertDropHost,
    QWidget#ConvertInfoHost,
    QWidget#ConvertActionHost,
    QWidget#ConvertBtnHost,
    QWidget#ConvertProgressHost,
    QWidget#ConvertStatusHost {{
        background: transparent;
    }}

    QLabel#ConvertSectionTitle {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 11px;
        font-weight: 700;
        color: {c['text_mute']};
        letter-spacing: 2px;
        background: transparent;
        padding-top: 4px;
    }}

    QLabel#ConvertFileLabel {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 12px;
        color: {c['text_dim']};
        background: transparent;
    }}

    QLabel#ConvertStatus {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 12px;
        color: {c['text_dim']};
        background: transparent;
    }}

    QLabel#ConvertStatus[state="ok"] {{
        color: {c['success']};
    }}

    QLabel#ConvertStatus[state="err"] {{
        color: {c['danger']};
    }}

    QComboBox#ConvertCombo {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        color: {c['text']};
        padding: 6px 12px;
        font-size: 13px;
        min-width: 160px;
    }}

    QComboBox#ConvertCombo:hover {{
        border-color: {c['accent_hi']};
    }}

    QComboBox#ConvertCombo::drop-down {{
        border: none;
        width: 24px;
    }}

    QComboBox#ConvertCombo::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {c['text_dim']};
        margin-right: 8px;
    }}

    QComboBox#ConvertCombo QAbstractItemView {{
        background-color: {c['card']};
        border: 1px solid {c['border']};
        color: {c['text']};
        selection-background-color: {c['accent']};
        selection-color: #FFFFFF;
        outline: none;
        padding: 4px;
    }}

    QSpinBox#ConvertSpin {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        color: {c['text']};
        padding: 6px 10px;
        font-size: 13px;
        min-width: 80px;
    }}

    QSpinBox#ConvertSpin:hover {{
        border-color: {c['accent_hi']};
    }}

    QToolButton#ConvertRunBtn {{
        background-color: {c['accent']};
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 8px 24px;
        font-size: 13px;
        font-weight: 600;
    }}

    QToolButton#ConvertRunBtn:hover {{
        background-color: {c['accent_hi']};
    }}

    QToolButton#ConvertRunBtn:pressed {{
        background-color: {c['accent']};
    }}

    QToolButton#ConvertRunBtn:disabled {{
        background-color: {c['border']};
        color: {c['text_mute']};
    }}
    QWidget#HexTopBar,
    QWidget#HexDropHost,
    QWidget#HexCtrlHost,
    QWidget#HexSearchHost,
    QWidget#HexNavHost,
    QWidget#HexViewHost {{
        background: transparent;
    }}

    QLabel#HexLabel {{
        font-size: 12px;
        color: {c['text_dim']};
        background: transparent;
    }}

    QLabel#HexInfo {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 12px;
        color: {c['text']};
        background: transparent;
    }}

    QLineEdit#HexInput {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        color: {c['text']};
        padding: 6px 10px;
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 12px;
    }}

    QLineEdit#HexInput:focus {{
        border-color: {c['accent']};
    }}

    QPlainTextEdit#HexView {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        color: {c['text']};
        padding: 12px;
        selection-background-color: {c['accent']};
        selection-color: #FFFFFF;
    }}
    QWidget#PermTopBar,
    QWidget#PermDropHost,
    QWidget#PermInfoHost,
    QWidget#PermUnixHost,
    QWidget#PermOctalHost,
    QWidget#PermWinHost,
    QWidget#PermGrid,
    QWidget#PermBtnHost,
    QWidget#PermStatusHost {{
        background: transparent;
    }}

    QLabel#PermModeLabel {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 13px;
        font-weight: 600;
        color: {c['accent']};
        background: transparent;
    }}

    QLabel#PermColumn {{
        font-size: 11px;
        font-weight: 700;
        color: {c['text_mute']};
        letter-spacing: 1px;
        background: transparent;
    }}

    QLabel#PermRow {{
        font-size: 12px;
        color: {c['text_dim']};
        background: transparent;
    }}

    QCheckBox#PermCheck {{
        background: transparent;
        color: {c['text']};
        font-size: 12px;
        spacing: 6px;
    }}

    QCheckBox#PermCheck::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 4px;
        border: 1.5px solid {c['border']};
        background: {c['card']};
    }}

    QCheckBox#PermCheck::indicator:hover {{
        border-color: {c['accent_hi']};
    }}

    QCheckBox#PermCheck::indicator:checked {{
        background-color: {c['accent']};
        border-color: {c['accent']};
    }}
    QWidget#RegexTopBar,
    QWidget#RegexDropHost,
    QWidget#RegexPatternHost,
    QWidget#RegexTabPage {{
        background: transparent;
    }}

    QLabel#RegexSlash {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 20px;
        font-weight: 700;
        color: {c['accent']};
        background: transparent;
        padding: 0 4px;
    }}

    QLineEdit#RegexInput {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        color: {c['text']};
        padding: 8px 12px;
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 13px;
    }}

    QLineEdit#RegexInput:focus {{
        border-color: {c['accent']};
    }}

    QCheckBox#RegexFlag {{
        background: transparent;
        color: {c['text_dim']};
        font-size: 12px;
        spacing: 6px;
    }}

    QCheckBox#RegexFlag::indicator {{
        width: 14px;
        height: 14px;
        border-radius: 3px;
        border: 1.5px solid {c['border']};
        background: {c['card']};
    }}

    QCheckBox#RegexFlag::indicator:checked {{
        background-color: {c['accent']};
        border-color: {c['accent']};
    }}

    QLabel#RegexStatus {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 11px;
        color: {c['text_mute']};
        background: transparent;
        padding: 0 6px;
    }}

    QLabel#RegexStatus[state="ok"] {{
        color: {c['success']};
    }}

    QLabel#RegexStatus[state="err"] {{
        color: {c['danger']};
    }}

    QLabel#RegexSectionLabel {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 10px;
        font-weight: 700;
        color: {c['text_mute']};
        letter-spacing: 2px;
        background: transparent;
    }}

    QPlainTextEdit#RegexSource {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        color: {c['text']};
        padding: 10px;
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 12px;
        selection-background-color: {c['accent']};
        selection-color: #FFFFFF;
    }}

    QTableWidget#RegexTable {{
        background-color: {c['bg']};
        alternate-background-color: {c['card_alt']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        color: {c['text']};
        gridline-color: {c['border']};
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 11px;
    }}

    QTableWidget#RegexTable::item {{
        padding: 4px 6px;
    }}

    QTableWidget#RegexTable::item:selected {{
        background-color: {c['accent']};
        color: #FFFFFF;
    }}

    QTableWidget#RegexTable QHeaderView::section {{
        background-color: {c['sidebar']};
        color: {c['text_dim']};
        border: none;
        border-bottom: 1px solid {c['border']};
        padding: 6px 8px;
        font-family: "Segoe UI", "Inter", sans-serif;
        font-size: 11px;
        font-weight: 600;
    }}

    QTabWidget#RegexTabs::pane {{
        background: transparent;
        border: none;
        border-top: 1px solid {c['border']};
    }}

    QTabWidget#RegexTabs QTabBar::tab {{
        background: transparent;
        color: {c['text_dim']};
        border: none;
        padding: 8px 16px;
        font-size: 12px;
        font-weight: 500;
    }}

    QTabWidget#RegexTabs QTabBar::tab:selected {{
        color: {c['accent']};
        border-bottom: 2px solid {c['accent']};
    }}

    QTabWidget#RegexTabs QTabBar::tab:hover {{
        color: {c['text']};
    }}

    QLabel#RegexHelp {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 12px;
        color: {c['text']};
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        padding: 16px;
        line-height: 1.6;
    }}
    QWidget#EncTopBar,
    QWidget#EncDropHost,
    QWidget#EncResultHost,
    QWidget#EncCandidatesHost,
    QWidget#EncPreviewHost,
    QWidget#EncConvertHost {{
        background: transparent;
    }}

    QLabel#EncFileLabel {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 12px;
        color: {c['text_dim']};
        background: transparent;
    }}

    QLabel#EncResult {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 14px;
        font-weight: 700;
        color: {c['accent']};
        background: transparent;
    }}

    QLabel#EncConfidence {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 12px;
        color: {c['text_mute']};
        background: transparent;
    }}

    QLabel#EncCandidate {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 11px;
        color: {c['text_dim']};
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 3px 8px;
    }}

    QPlainTextEdit#EncPreview {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        color: {c['text']};
        padding: 10px;
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 12px;
        selection-background-color: {c['accent']};
        selection-color: #FFFFFF;
    }}
    QWidget#SqliteTopBar,
    QWidget#SqliteDropHost,
    QWidget#SqliteMainHost {{
        background: transparent;
    }}

    QListWidget#SqliteTables {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        color: {c['text']};
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 12px;
        padding: 4px;
        outline: none;
    }}

    QListWidget#SqliteTables::item {{
        padding: 6px 8px;
        border-radius: 6px;
    }}

    QListWidget#SqliteTables::item:hover {{
        background-color: {c['accent_lo']};
    }}

    QListWidget#SqliteTables::item:selected {{
        background-color: {c['accent']};
        color: #FFFFFF;
    }}

    QTableWidget#SqliteDataTable,
    QTableWidget#SqliteSchemaTable {{
        background-color: {c['bg']};
        alternate-background-color: {c['card_alt']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        color: {c['text']};
        gridline-color: {c['border']};
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 11px;
    }}

    QTableWidget#SqliteDataTable::item,
    QTableWidget#SqliteSchemaTable::item {{
        padding: 3px 6px;
    }}

    QTableWidget#SqliteDataTable::item:selected,
    QTableWidget#SqliteSchemaTable::item:selected {{
        background-color: {c['accent']};
        color: #FFFFFF;
    }}

    QTableWidget#SqliteDataTable QHeaderView::section,
    QTableWidget#SqliteSchemaTable QHeaderView::section {{
        background-color: {c['sidebar']};
        color: {c['text_dim']};
        border: none;
        border-bottom: 1px solid {c['border']};
        padding: 5px 8px;
        font-family: "Segoe UI", "Inter", sans-serif;
        font-size: 11px;
        font-weight: 600;
    }}

    QPlainTextEdit#SqliteSqlInput {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        color: {c['text']};
        padding: 10px;
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 12px;
        selection-background-color: {c['accent']};
        selection-color: #FFFFFF;
    }}
    QWidget#PwdTopBar {{
        background: transparent;
    }}

    QPlainTextEdit#PwdOutput {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 12px;
        color: {c['text']};
        padding: 12px 16px;
        selection-background-color: {c['accent']};
        selection-color: #FFFFFF;
    }}

    QProgressBar#PwdStrength {{
        background-color: {c['border']};
        border: none;
        border-radius: 3px;
    }}

    QProgressBar#PwdStrength::chunk {{
        background-color: {c['danger']};
        border-radius: 3px;
    }}

    QProgressBar#PwdStrength[score="1"]::chunk {{
        background-color: #C9A76B;
    }}

    QProgressBar#PwdStrength[score="2"]::chunk {{
        background-color: {c['warning']};
    }}

    QProgressBar#PwdStrength[score="3"]::chunk {{
        background-color: {c['accent']};
    }}

    QProgressBar#PwdStrength[score="4"]::chunk {{
        background-color: {c['success']};
    }}

    QLabel#PwdStrengthLabel {{
        font-family: "Consolas", "JetBrains Mono", "Menlo", monospace;
        font-size: 11px;
        font-weight: 600;
        color: {c['text_mute']};
        background: transparent;
    }}

    QLabel#PwdStrengthLabel[score="1"] {{ color: #C9A76B; }}
    QLabel#PwdStrengthLabel[score="2"] {{ color: {c['warning']}; }}
    QLabel#PwdStrengthLabel[score="3"] {{ color: {c['accent']}; }}
    QLabel#PwdStrengthLabel[score="4"] {{ color: {c['success']}; }}

    QSlider#PwdSlider::groove:horizontal {{
        background-color: {c['border']};
        height: 4px;
        border-radius: 2px;
    }}

    QSlider#PwdSlider::sub-page:horizontal {{
        background-color: {c['accent']};
        height: 4px;
        border-radius: 2px;
    }}

    QSlider#PwdSlider::handle:horizontal {{
        background-color: {c['accent']};
        border: 2px solid {c['card']};
        width: 14px;
        height: 14px;
        margin: -6px 0;
        border-radius: 8px;
    }}

    QSlider#PwdSlider::handle:horizontal:hover {{
        background-color: {c['accent_hi']};
    }}
    QWidget#FontTopBar,
    QWidget#FontDropHost,
    QWidget#FontSelectorHost,
    QWidget#FontUnicodeHost {{
        background: transparent;
    }}

    QFrame#FontPreviewHost {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 12px;
    }}

    QLabel#FontPreviewText {{
        color: {c['text']};
        background: transparent;
    }}
    QWidget#SearchChipsHost {{
        background: transparent;
    }}

    QPushButton#SearchChip {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 14px;
        color: {c['text_dim']};
        font-size: 12px;
        font-weight: 500;
        padding: 5px 14px;
        min-height: 24px;
    }}

    QPushButton#SearchChip:hover {{
        background-color: {c['accent_lo']};
        border-color: {c['accent_hi']};
        color: {c['text']};
    }}

    QPushButton#SearchChip:checked {{
        background-color: {c['accent']};
        border-color: {c['accent']};
        color: #FFFFFF;
    }}

    QPushButton#SearchChip:checked:hover {{
        background-color: {c['accent_hi']};
    }}
    QWidget#ExifTopBar,
    QWidget#ExifDropHost,
    QWidget#ExifMainHost,
    QWidget#ExifOptsHost {{
        background: transparent;
    }}
    QWidget#QrTopBar {{
        background: transparent;
    }}

    QFrame#QrPreviewHost {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 12px;
    }}

    QLabel#QrPreview {{
        color: {c['text_dim']};
        font-size: 13px;
        background: transparent;
    }}

    QFrame#QrResultCard {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 10px;
    }}
    QWidget#StegoTopBar {{
        background: transparent;
    }}
    QWidget#B64TopBar {{
        background: transparent;
    }}
        QWidget#QuickGridHost {{
        background: transparent;
    }}

    QFrame#QuickCard {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 12px;
    }}

    QFrame#QuickCard:hover {{
        background-color: {c['accent_lo']};
        border-color: {c['accent_hi']};
    }}

    QLabel#QuickCardName {{
        font-family: "Segoe UI", "Inter", sans-serif;
        font-size: 14px;
        font-weight: 600;
        color: {c['text']};
        background: transparent;
    }}

    QLabel#QuickCardDesc {{
        font-family: "Segoe UI", "Inter", sans-serif;
        font-size: 12px;
        color: {c['text_dim']};
        background: transparent;
    }}

    QToolButton#QuickRefreshBtn {{
        background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        color: {c['text_dim']};
        font-size: 12px;
        padding: 5px 12px;
    }}

    QToolButton#QuickRefreshBtn:hover {{
        background-color: {c['accent_lo']};
        border-color: {c['accent_hi']};
        color: {c['accent']};
    }}
    """


def qss_for(name: str) -> str:
    return build_qss(LIGHT if name == "light" else DARK)