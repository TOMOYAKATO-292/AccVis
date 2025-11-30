def get_google_cloud_css():
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #3C4043;
        }

        /* Main Background */
        .stApp {
            background-color: #F8F9FA;
        }

        /* Hide default Streamlit header decoration */
        header {
            visibility: hidden;
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
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            margin-bottom: 24px;
            border: 1px solid #E8EAED;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E8EAED;
        }
        
        /* Sidebar Headers */
        .sidebar-header {
            font-size: 0.9rem;
            font-weight: 600;
            color: #202124;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }

        /* Metrics */
        div[data-testid="stMetric"] {
            background-color: #FFFFFF;
            padding: 16px;
            border-radius: 12px;
            border: 1px solid #E8EAED;
            box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3);
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.9rem;
            color: #5F6368;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            font-weight: 600;
            color: #1A73E8;
        }

        /* Buttons */
        div.stButton > button[kind="primary"] {
            background-color: #1A73E8;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 500;
            padding: 0.6rem 1.2rem;
            box-shadow: 0 1px 2px rgba(60,64,67,0.3);
            transition: all 0.2s;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #1765CC;
            box-shadow: 0 2px 4px rgba(60,64,67,0.3);
            transform: translateY(-1px);
        }
        
        div.stButton > button[kind="secondary"] {
            background-color: white;
            color: #3C4043;
            border: 1px solid #DADCE0;
            border-radius: 8px;
            font-weight: 500;
        }

        /* Dataframes */
        div[data-testid="stDataFrame"] {
            border: 1px solid #E8EAED;
            border-radius: 8px;
            overflow: hidden;
        }

        /* Custom Classes for injection */
        .dashboard-card-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #202124;
            margin-bottom: 1rem;
        }
        
    </style>
    """
