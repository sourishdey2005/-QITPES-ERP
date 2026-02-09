def load_css():
    return """
    <style>
        /* --- GLOBAL BRANDING: BLUE & WHITE --- */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #ffffff !important;
        }

        /* Force Black text on white background for primary readability */
        .stApp, p, span, label, .stMarkdown, div {
            color: #000000 !important;
        }

        /* --- HEADERS: BLUE ACCENTS --- */
        h1, h2, h3 {
            color: #1e3a8a !important; /* Deep Blue for Headers */
            border-bottom: 2px solid #3b82f6 !important; /* Light Blue Underline */
            padding-bottom: 5px;
            margin-bottom: 20px !important;
        }

        /* --- BUTTONS: TRANSPARENT WHITE WITH BLUE TEXT --- */
        button, .stButton>button, .stDownloadButton>button, button[kind="primary"], button[kind="secondary"] {
            background-color: transparent !important;
            color: #3b82f6 !important; /* Blue Text */
            border: 2px solid #3b82f6 !important; /* Blue Border */
            border-radius: 8px !important;
            font-weight: bold !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 10px 20px !important;
            transition: 0.3s all ease !important;
        }

        button:hover {
            background-color: #3b82f6 !important; /* Solid Blue on hover */
            color: #ffffff !important; /* White Text on hover */
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
        }
        /* --- DROPDOWNS & SELECTBOXES: CLEAN WHITE/BLUE --- */
        /* Main Selectbox Container */
        div[data-testid="stSelectbox"] [data-baseweb="select"] {
            background-color: #ffffff !important;
            border: 1px solid #3b82f6 !important;
            border-radius: 8px !important;
        }

        /* Current Selected Text */
        div[data-testid="stSelectbox"] [data-baseweb="select"] * {
            color: #3b82f6 !important;
            background-color: transparent !important;
        }

        /* Arrow Icon */
        div[data-testid="stSelectbox"] svg {
            fill: #3b82f6 !important;
        }

        /* --- THE POPUP MENU (DROPDOWN OPTIONS) --- */
        /* This targets the floating list that opens up */
        ul[data-baseweb="menu"], div[role="listbox"] {
            background-color: #ffffff !important;
            border: 2px solid #3b82f6 !important;
            border-radius: 8px !important;
        }

        /* Individual Options */
        li[data-baseweb="option"], [role="option"] {
            background-color: #ffffff !important;
            color: #000000 !important;
            padding: 10px !important;
        }

        /* Active/Hovered Option */
        li[data-baseweb="option"]:hover, [role="option"]:hover, li[aria-selected="true"] {
            background-color: #3b82f6 !important;
            color: #ffffff !important;
        }

        /* Navigation Label (Text above dropdown) */
        div[data-testid="stSelectbox"] label p {
            color: #000000 !important;
            font-weight: bold !important;
        }

        /* --- METRICS (KPIs): BLUE CARDS --- */
        div[data-testid="stMetric"] {
            background-color: #3b82f6 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            border: 1px solid #1e40af !important;
        }

        div[data-testid="stMetricLabel"] > div {
            color: #ffffff !important;
            font-weight: 600 !important;
        }

        div[data-testid="stMetricValue"] > div {
            color: #ffffff !important;
            font-weight: 900 !important;
        }

        /* --- SIDEBAR: CLEAN WHITE --- */
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 3px solid #3b82f6 !important;
        }

        /* Sidebar Navigation Items */
        [data-testid="stSidebarNav"] * {
            color: #1e3a8a !important;
            font-weight: 600 !important;
        }

        /* --- TABS: BLUE THEME --- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #f0f7ff !important;
            border: 1px solid #3b82f6 !important;
            color: #3b82f6 !important;
            border-radius: 8px 8px 0 0 !important;
            padding: 10px 20px !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #3b82f6 !important;
            color: #ffffff !important;
        }

        /* --- INPUTS & TEXT AREAS: WHITE BACKGROUND & BLUE BORDER --- */
        input, textarea, [data-testid="stTextInput"] div[data-baseweb="input"], [data-testid="stTextArea"] div[data-baseweb="base-input"] {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #3b82f6 !important;
            border-radius: 8px !important;
        }

        /* Target the actual inner input element */
        input, textarea {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        /* Focus state */
        input:focus, textarea:focus {
            outline: none !important;
            border: 2px solid #1e40af !important;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2) !important;
        }

        /* Labels for inputs */
        div[data-testid="stTextInput"] label, div[data-testid="stTextArea"] label {
            color: #1e3a8a !important;
            font-weight: 600 !important;
        }

        /* Password eye icon color */
        span[data-testid="InputAdornment"] path {
            fill: #3b82f6 !important;
        }

        /* --- HEADER (TOP BAR): CLEAN WHITE THEME --- */
        header[data-testid="stHeader"] {
            background-color: #ffffff !important;
            border-bottom: 1px solid #e5e7eb !important;
        }

        /* Top Bar Buttons (Deploy, Menu, Sidebar Toggle) */
        header[data-testid="stHeader"] button {
            background-color: transparent !important;
            color: #3b82f6 !important;
            border: 1px solid #3b82f6 !important;
            border-radius: 4px !important;
        }

        header[data-testid="stHeader"] svg {
            fill: #3b82f6 !important;
        }

        /* --- TABLES & DATAFRAMES --- */
        .dataframe {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        .dataframe thead th {
            background-color: #3b82f6 !important;
            color: #ffffff !important;
        }

        /* --- EXPANDERS: WHITE BACKGROUND & BLUE BORDER --- */
        details {
            background-color: #ffffff !important;
            border: 1px solid #3b82f6 !important;
            border-radius: 8px !important;
            margin-bottom: 10px !important;
        }
        summary {
            background-color: #f0f7ff !important;
            color: #1e3a8a !important;
            font-weight: bold !important;
            padding: 10px !important;
            border-radius: 8px 8px 0 0 !important;
        }
        summary:hover {
            background-color: #3b82f6 !important;
            color: #ffffff !important;
        }
        /* Expander content */
        details > div {
            background-color: #ffffff !important;
            color: #000000 !important;
            padding: 15px !important;
        }

        /* --- STATUS MESSAGES (Alerts) --- */
        div[data-testid="stNotification"] {
            background-color: #f0f7ff !important;
            color: #1e3a8a !important;
            border: 1px solid #3b82f6 !important;
            border-radius: 8px !important;
        }
        div[data-testid="stNotification"] svg {
            fill: #3b82f6 !important;
        }

        /* --- DIVIDERS & CAPTIONS --- */
        hr {
            border-top: 1px solid #3b82f6 !important;
            opacity: 0.3;
        }
        .stCaption {
            color: #1e3a8a !important;
            font-style: italic;
        }
    </style>
    """
