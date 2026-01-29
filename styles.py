def get_custom_css(language='ar'):
    alignment = "right" if language == 'ar' else "left"
    direction = "rtl" if language == 'ar' else "ltr"
    
    # Using Bootstrap-like colors from the reference project
    primary_color = "#1b6ec2" # Corporate blue from .NET project
    secondary_color = "#6c757d"
    bg_color = "#f8f9fa" # Light gray/white background
    card_bg = "#ffffff"
    text_color = "#212529"
    coffee_accent = "#6F4E37"

    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Arabic:wght@400;600;700&family=Inter:wght@400;600;700&display=swap');

    .stApp {{
        background-color: {bg_color};
        font-family: { "'IBM Plex Arabic', sans-serif" if language == 'ar' else "'Inter', sans-serif" };
        direction: {direction};
    }}

    /* Global text alignment */
    .stMarkdown, .stText, .stAlert, .stSelectbox, .stTextInput, .stNumberInput, .stTextArea, .stButton {{
        direction: {direction} !important;
        text-align: {alignment} !important;
    }}

    /* Sidebar Styling - Modern Dark or Clean White? Let's go Clean White like the .NET project */
    [data-testid="stSidebar"] {{
        background-color: white;
        border-right: 1px solid #dee2e6;
    }}
    
    [data-testid="stSidebar"] .stMarkdown h1 {{
        color: {primary_color} !important;
        font-size: 1.5rem !important;
    }}

    /* Title & Headers */
    h1, h2, h3 {{
        color: {text_color};
        font-weight: 700;
        margin-bottom: 1rem;
    }}

    /* Buttons - Matching the .NET project primary blue */
    .stButton>button {{
        background-color: {primary_color};
        color: white;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        width: 100%;
        transition: 0.2s;
    }}
    .stButton>button:hover {{
        background-color: #155a9c;
        color: white;
        border: none;
    }}

    /* Inputs */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input, .stTextArea>div>div>textarea {{
        border-radius: 4px !important;
        border: 1px solid #ced4da !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background-color: transparent;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        background-color: white;
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
        border: 1px solid #dee2e6;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: white !important;
        border-bottom: 2px solid {primary_color} !important;
        color: {primary_color} !important;
    }}

    /* Metrics */
    [data-testid="stMetric"] {{
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}

    /* Dataframe */
    .stDataFrame {{
        border: 1px solid #dee2e6;
        border-radius: 8px;
    }}

    /* Footer */
    .footer {{
        text-align: center;
        padding: 2rem;
        color: {secondary_color};
        font-size: 0.9rem;
        border-top: 1px solid #dee2e6;
        margin-top: 3rem;
    }}

    </style>
    """

def card_html(content, title=None):
    # This function is now deprecated to avoid broken HTML injection in Streamlit
    return ""
