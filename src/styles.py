def get_google_cloud_css():
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Space Grotesk', sans-serif;
            color: #3C4043;
        }
        
        code, pre, .monospace {
            font-family: 'Space Mono', monospace;
        }

        /* Main Background */
        .stApp {
            background-color: #F8F9FA;
        }

        /* Header Styling */
        header[data-testid="stHeader"] {
            background-color: transparent;
        }
        
        /* Custom Title Styling */
        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #202124;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            font-size: 1.1rem;
            color: #5F6368;
            margin-bottom: 2rem;
        }

        /* Card Styling */
        .css-card {
            background-color: #FFFFFF;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            margin-bottom: 24px;
            border: 1px solid #F1F3F4;
            transition: all 0.3s ease;
        }
        .css-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
        }

        /* Metric Card Styling */
        .css-metric-card {
            background-color: #FFFFFF;
            border-radius: 16px;
            padding: 20px;
            border: 1px solid #F1F3F4;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            transition: all 0.3s ease;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .css-metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.08);
            border-color: #E8F0FE;
        }
        
        .metric-label {
            font-size: 0.85rem;
            font-weight: 600;
            color: #5F6368;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #202124;
            line-height: 1.2;
        }
        
        .metric-icon {
            font-size: 1.5rem;
            margin-bottom: 12px;
            color: #1A73E8;
            background-color: #E8F0FE;
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E8EAED;
        }
        
        /* Sidebar Headers */
        .sidebar-header {
            font-size: 0.85rem;
            font-weight: 700;
            color: #202124;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 1.5rem;
            margin-bottom: 0.8rem;
        }

        /* Hide default metrics to use custom ones */
        div[data-testid="stMetric"] {
            display: none;
        }

        /* Buttons */
        div.stButton > button[kind="primary"] {
            background-color: #1A73E8;
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 0.6rem 1.2rem;
            box-shadow: 0 2px 4px rgba(26, 115, 232, 0.2);
            transition: all 0.2s;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #1765CC;
            box-shadow: 0 4px 8px rgba(26, 115, 232, 0.3);
            transform: translateY(-1px);
        }
        
        div.stButton > button[kind="secondary"] {
            background-color: white;
            color: #3C4043;
            border: 1px solid #DADCE0;
            border-radius: 10px;
            font-weight: 500;
        }
        div.stButton > button[kind="secondary"]:hover {
            background-color: #F8F9FA;
            border-color: #3C4043;
        }

        /* Dataframes */
        div[data-testid="stDataFrame"] {
            border: 1px solid #E8EAED;
            border-radius: 12px;
            overflow: hidden;
        }

        /* Custom Classes for injection */
        .dashboard-card-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #202124;
            margin-bottom: 1.2rem;
        }
        
    </style>
    """
