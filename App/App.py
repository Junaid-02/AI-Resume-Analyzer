import streamlit as st # core package used in this project
import pandas as pd
import base64, random
import time,datetime
# import pymysql
import os
import socket
import platform
import geocoder
import secrets
import io,random
import plotly.express as px # to create visualisations at the admin session
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
# libraries used to parse the pdf files
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
# pre stored data for prediction purposes
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
import nltk
nltk.download('stopwords')
import re

def save_to_excel(data, filename='User_Data.xlsx', sheet_name='Sheet1'):
    from openpyxl import load_workbook
    if os.path.exists(filename):
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            try:
                df_existing = pd.read_excel(filename, sheet_name=sheet_name)
                df_new = pd.DataFrame([data]) if isinstance(data, dict) else pd.DataFrame(data)
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            except ValueError:
                df_combined = pd.DataFrame([data]) if isinstance(data, dict) else pd.DataFrame(data)
            df_combined.to_excel(writer, index=False, sheet_name=sheet_name)
    else:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df_combined = pd.DataFrame([data]) if isinstance(data, dict) else pd.DataFrame(data)
            df_combined.to_excel(writer, index=False, sheet_name=sheet_name)

def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)

def is_valid_phone(phone):
    return phone.isdigit() and 10 <= len(phone) <= 15

def is_duplicate_entry(email, phone, filename='User_Data.xlsx', sheet_name='Sheet1'):
    import pandas as pd
    import os
    if not os.path.exists(filename):
        return False
    try:
        df = pd.read_excel(filename, sheet_name=sheet_name)
        if 'Mail' in df.columns and email in df['Mail'].astype(str).values:
            return True
        if 'Mobile Number' in df.columns and phone in df['Mobile Number'].astype(str).values:
            return True
    except Exception:
        return False
    return False

def mask_email(email):
    if not isinstance(email, str) or '@' not in email:
        return email
    user, domain = email.split('@', 1)
    if len(user) > 2:
        user_masked = user[0] + '*'*(len(user)-2) + user[-1]
    else:
        user_masked = user[0] + '*'
    domain_parts = domain.split('.')
    domain_masked = domain_parts[0][0] + '*'*(len(domain_parts[0])-2) + domain_parts[0][-1] if len(domain_parts[0]) > 2 else domain_parts[0][0] + '*'
    return f"{user_masked}@{domain_masked}.{'.'.join(domain_parts[1:])}" if len(domain_parts) > 1 else f"{user_masked}@{domain_masked}"

def mask_phone(phone):
    phone = str(phone)
    if len(phone) < 7:
        return phone
    return phone[:2] + '*'*(len(phone)-4) + phone[-2:]

st.set_page_config(
   page_title="AI Resume Analyzer",
   page_icon='./Logo/recommend.png',
   layout="wide",
)

# Add global CSS to force all text, headers, and markdown to be visible on the light background
st.markdown(
    """
    <style>
    body, .stApp, .stMarkdown, .stText, .stHeader, .stSubheader, .stSuccess, .stWarning, .stInfo, .stError, .stDataFrame, .stTable, .stTextInput, .stTextArea, .stSelectbox, .stRadio, .stCheckbox, .stSlider, .stNumberInput, .stDateInput, .stTimeInput, .stColorPicker, .stFileUploader, .stButton, .stDownloadButton, .stForm, .stFormSubmitButton, .stExpander, .stTabs, .stTab, .stAlert, .stTooltip, .stPopover, .stBadge, .stLabel, .stCaption, .stCode, .stJson, .stLatex, .stMarkdown, .stText, .stHeader, .stSubheader, .stSuccess, .stWarning, .stInfo, .stError {
        color: #222 !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #2f8d46 !important;
        font-weight: bold !important;
    }
    .stText, .stHeader, .stSubheader, .stSuccess, .stWarning, .stInfo, .stError {
        color: #222 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Update global CSS for cream background and clear text
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #fffbe6 !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #2f8d46 !important;
        font-weight: bold !important;
    }
    .stText, .stHeader, .stSubheader, .stSuccess, .stWarning, .stInfo, .stError, .stMarkdown, .stDataFrame, .stTable {
        color: #222 !important;
        font-weight: bold !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- GLOBAL CSS ---
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #fffbe6 !important;
    }
    .stMarkdown, .stText, .stHeader, .stSubheader, .stSuccess, .stWarning, .stInfo, .stError, .stDataFrame, .stTable {
        color: #222 !important;
        font-weight: normal !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #2f8d46 !important;
        font-weight: bold !important;
        background: none !important;
    }
    label, .css-1cpxqw2, .css-1n76uvr, .css-1v0mbdj, .css-1y4p8pa {
        color: #222 !important;
        font-weight: bold !important;
    }
    .stButton>button {
        background-color: #2f8d46 !important;
        color: #fff !important;
        border-radius: 6px !important;
        border: none !important;
        font-weight: bold !important;
        padding: 0.5em 1.5em !important;
    }
    .stButton>button:hover {
        background-color: #1e5631 !important;
        color: #ffd700 !important;
    }
    .stSidebar, .css-1d391kg, .css-18e3th9, .st-bw, .st-cq, .st-dg, .st-dh, .st-dj, .st-dk, .st-dl, .st-dm, .st-dn, .st-do, .st-dp, .st-dq, .st-dr, .st-ds, .st-dt, .st-du, .st-dv, .st-dw, .st-dx, .st-dy, .st-dz, .st-e0, .st-e1, .st-e2, .st-e3, .st-e4, .st-e5, .st-e6, .st-e7, .st-e8, .st-e9, .st-ea, .st-eb, .st-ec, .st-ed, .st-ee, .st-ef, .st-eg, .st-eh, .st-ei, .st-ej, .st-ek, .st-el, .st-em, .st-en, .st-eo, .st-ep, .st-eq, .st-er, .st-es, .st-et, .st-eu, .st-ev, .st-ew, .st-ex, .st-ey, .st-ez, .st-f0, .st-f1, .st-f2, .st-f3, .st-f4, .st-f5, .st-f6, .st-f7, .st-f8, .st-f9, .st-fa, .st-fb, .st-fc, .st-fd, .st-fe, .st-ff, .st-fg, .st-fh, .st-fi, .st-fj, .st-fk, .st-fl, .st-fm, .st-fn, .st-fo, .st-fp, .st-fq, .st-fr, .st-fs, .st-ft, .st-fu, .st-fv, .st-fw, .st-fx, .st-fy, .st-fz, .st-g0, .st-g1, .st-g2, .st-g3, .st-g4, .st-g5, .st-g6, .st-g7, .st-g8, .st-g9, .st-ga, .st-gb, .st-gc, .st-gd, .st-ge, .st-gf, .st-gg, .st-gh, .st-gi, .st-gj, .st-gk, .st-gl, .st-gm, .st-gn, .st-go, .st-gp, .st-gq, .st-gr, .st-gs, .st-gt, .st-gu, .st-gv, .st-gw, .st-gx, .st-gy, .st-gz, .st-h0, .st-h1, .st-h2, .st-h3, .st-h4, .st-h5, .st-h6, .st-h7, .st-h8, .st-h9, .st-ha, .st-hb, .st-hc, .st-hd, .st-he, .st-hf, .st-hg, .st-hh, .st-hi, .st-hj, .st-hk, .st-hl, .st-hm, .st-hn, .st-ho, .st-hp, .st-hq, .st-hr, .st-hs, .st-ht, .st-hu, .st-hv, .st-hw, .st-hx, .st-hy, .st-hz { color: #222 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Update sidebar CSS for classic look and visibility
st.markdown(
    """
    <style>
    /* Sidebar heading */
    .css-1d391kg, .css-18e3th9, .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5, .stSidebar h6 {
        color: #2f8d46 !important;
        font-weight: bold !important;
    }
    /* Sidebar normal text, labels, captions, links */
    .stSidebar, .stSidebar p, .stSidebar label, .stSidebar span, .stSidebar a, .css-1v0mbdj, .css-1y4p8pa, .css-1n76uvr {
        color: #222 !important;
        font-weight: normal !important;
        background: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Fix selectbox dropdown: white background, dark text for all options
st.markdown(
    """
    <style>
    .stSelectbox [data-baseweb="select"] > div {
        background: #222 !important;
        color: #fff !important;
    }
    .stSelectbox [data-baseweb="select"] span {
        color: #fff !important;
    }
    .stSelectbox [data-baseweb="select"] div[role="option"] {
        background: #222 !important;
        color: #fff !important;
    }
    .stSelectbox [data-baseweb="select"] div[aria-selected="true"],
    .stSelectbox [data-baseweb="select"] div[aria-selected="true"]:hover {
        background: #444 !important;
        color: #fff !important;
    }
    .stSelectbox [data-baseweb="select"] div[aria-selected="false"]:hover {
        background: #333 !important;
        color: #fff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Update input and selectbox CSS for visible text and backgrounds
st.markdown(
    """
    <style>
    /* Input placeholder text color */
    input::placeholder, textarea::placeholder {
        color: #222 !important;
        opacity: 1 !important;
    }
    /* Input text color */
    .stTextInput>div>div>input, .stTextInput>div>div>div>input {
        color: #222 !important;
        background: #fff !important;
    }
    /* Selectbox dropdown background and text color */
    .stSelectbox [data-baseweb="select"] > div {
        background: #fff !important;
        color: #222 !important;
    }
    .stSelectbox [data-baseweb="select"] span {
        color: #222 !important;
    }
    .stSelectbox [data-baseweb="select"] div[role="option"] {
        background: #fff !important;
        color: #222 !important;
    }
    .stSelectbox [data-baseweb="select"] div[aria-selected="true"],
    .stSelectbox [data-baseweb="select"] div[aria-selected="true"]:hover {
        background: #e6e6e6 !important;
        color: #222 !important;
    }
    .stSelectbox [data-baseweb="select"] div[aria-selected="false"]:hover {
        background: #f0f0f0 !important;
        color: #222 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Add to global CSS for green submit button
st.markdown(
    """
    <style>
    .stForm button[type="submit"], .stButton>button {
        background-color: #2f8d46 !important;
        color: #fff !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
        padding: 0.5em 2em !important;
        box-shadow: none !important;
    }
    .stForm button[type="submit"]:hover, .stButton>button:hover {
        background-color: #1e5631 !important;
        color: #ffd700 !important;
    }
    .stForm button[type="submit"][disabled], .stButton>button[disabled] {
        background-color: #2f8d46 !important;
        color: #fff !important;
        opacity: 0.5 !important;
        border: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

###### Preprocessing functions ######


# Generates a link allowing the data in a given panda dataframe to be downloaded in csv format 
def get_csv_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    ## bytes conversions
    b64 = base64.b64encode(csv.encode()).decode()      
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


# Reads Pdf file and check_extractable
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    ## close open handles
    converter.close()
    fake_file_handle.close()
    return text


# show uploaded file path to view pdf_display
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# course recommendations which has data already loaded from Courses.py
def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 👨‍🎓**")
    c = 0
    rec_course = []
    ## slider to choose from range 1-10
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course


###### Database Stuffs ######


# In-memory storage for demo/testing
user_data_list = []
user_feedback_list = []


# inserting miscellaneous data, fetched results, prediction and recommendation into user_data table
def insert_data(sec_token,ip_add,host_name,dev_user,os_name_ver,latlong,city,state,country,act_name,act_mail,act_mob,name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses,pdf_name):
    user_data_list.append({
        'sec_token': sec_token,
        'ip_add': ip_add,
        'host_name': host_name,
        'dev_user': dev_user,
        'os_name_ver': os_name_ver,
        'latlong': latlong,
        'city': city,
        'state': state,
        'country': country,
        'act_name': act_name,
        'act_mail': act_mail,
        'act_mob': act_mob,
        'name': name,
        'email': email,
        'res_score': res_score,
        'timestamp': timestamp,
        'no_of_pages': no_of_pages,
        'reco_field': reco_field,
        'cand_level': cand_level,
        'skills': skills,
        'recommended_skills': recommended_skills,
        'courses': courses,
        'pdf_name': pdf_name
    })


# inserting feedback data into user_feedback table
def insertf_data(feed_name,feed_email,feed_score,comments,Timestamp):
    user_feedback_list.append({
        'feed_name': feed_name,
        'feed_email': feed_email,
        'feed_score': feed_score,
        'comments': comments,
        'Timestamp': Timestamp
    })


###### Setting Page Configuration (favicon, Logo, Title) ######





###### Main function run() ######


def run():
    
    # (Logo, Heading, Sidebar etc)
    img = Image.open('./Logo/RESUM.png')
    st.image(img)
    st.sidebar.markdown("# Choose Something...")
    activities = ["User", "Feedback", "About", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    link = '<b>Built by <a href="https://www.linkedin.com/in/mohammed-junaid-dob25042004/" style="text-decoration: underline; color: #fff;">Mohammed Junaid</a></b>'
    st.sidebar.markdown(link, unsafe_allow_html=True)
    st.sidebar.markdown('''
        <!-- site visitors -->

        <div id="sfct2xghr8ak6lfqt3kgru233378jya38dy" hidden></div>

        <noscript>
            <a href="https://www.freecounterstat.com" title="hit counter">
                <img src="https://counter9.stat.ovh/private/freecounterstat.php?c=t2xghr8ak6lfqt3kgru233378jya38dy" border="0" title="hit counter" alt="hit counter"> -->
            </a>
        </noscript>
    
        <p>Visitors <img src="https://counter9.stat.ovh/private/freecounterstat.php?c=t2xghr8ak6lfqt3kgru233378jya38dy" title="Free Counter" Alt="web counter" width="60px"  border="0" /></p>
    
    ''', unsafe_allow_html=True)

    ###### Creating Database and Table ######


    # Remove DB/table creation code
    # db_sql = ...
    # cursor.execute(db_sql)
    # ...
    # table_sql = ...
    # cursor.execute(table_sql)
    # ...
    # tablef_sql = ...
    # cursor.execute(tablef_sql)


    ###### CODE FOR CLIENT SIDE (USER) ######

    if choice == 'User':
        
        # Collecting Miscellaneous Information
        st.markdown('<h2 style="color:#2f8d46; font-weight:bold;">Please fill in your details below to get personalized resume analysis and recommendations.</h2>', unsafe_allow_html=True)
        act_name = st.text_input('Name*', placeholder='Enter your full name', help='Please enter your legal name as it appears on your resume.')
        act_mail = st.text_input('Mail*', placeholder='Enter your email address', help="We'll use this to contact you with recommendations.")
        act_mob  = st.text_input('Mobile Number*', placeholder='Enter your mobile number', help='Include country code if outside India.')
        sec_token = secrets.token_urlsafe(12)
        host_name = socket.gethostname()
        ip_add = socket.gethostbyname(host_name)
        dev_user = os.getlogin()
        os_name_ver = platform.system() + " " + platform.release()
        g = geocoder.ip('me')
        latlong = g.latlng
        geolocator = Nominatim(user_agent="http")
        location = geolocator.reverse(latlong, language='en')
        address = location.raw['address']
        cityy = address.get('city', '')
        statee = address.get('state', '')
        countryy = address.get('country', '')  
        city = cityy
        state = statee
        country = countryy


        # Upload Resume
        st.markdown('<h3 style="color:#2f8d46; font-weight:bold; margin-top:2em;">Upload Your Resume, And Get Smart Recommendations</h3>', unsafe_allow_html=True)
        
        ## file upload in pdf format
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            try:
                with st.spinner('Hang On While We Cook Magic For You...'):
                    time.sleep(2)
                save_image_path = './Uploaded_Resumes/' + pdf_file.name
                pdf_name = pdf_file.name
                with open(save_image_path, "wb") as f:
                    f.write(pdf_file.getbuffer())
                show_pdf(save_image_path)
            except Exception as e:
                st.error(f"Error uploading or saving the file: {e}")
                st.stop()
            try:
                resume_data = ResumeParser(save_image_path).get_extracted_data()
            except Exception as e:
                st.error(f"Error parsing the resume: {e}")
                st.stop()
            if resume_data:
                
                ## Get the whole resume data into resume_text
                resume_text = pdf_reader(save_image_path)

                ## Showing Analyzed data from (resume_data)
                st.markdown('<h1 style="color:#2f8d46; font-weight:bold;">Resume Analysis 🤘</h1>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#2f8d46; font-weight:bold;">Hello {resume_data["name"].upper()}</div>', unsafe_allow_html=True)
                st.markdown('<h2 style="color:#2f8d46; font-weight:bold;">Your Basic Info 👀</h2>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#222; font-size:1.1em; font-weight:bold;">Name: {resume_data["name"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#222; font-size:1.1em; font-weight:bold;">Email: {resume_data["email"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#222; font-size:1.1em; font-weight:bold;">Contact: {resume_data["mobile_number"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#222; font-size:1.1em; font-weight:bold;">Degree: {str(resume_data["degree"])} </div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#222; font-size:1.1em; font-weight:bold;">Resume pages: {str(resume_data["no_of_pages"])} </div>', unsafe_allow_html=True)

                ## Predicting Candidate Experience Level 

                ### Trying with different possibilities
                cand_level = ''
                if resume_data['no_of_pages'] < 1:                
                    cand_level = "NA"
                    st.markdown('<div style="color:#d73b5c; font-weight:bold;">❌ You are at Fresher level!</div>', unsafe_allow_html=True)
                
                #### if internship then intermediate level
                elif 'INTERNSHIP' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'INTERNSHIPS' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internship' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internships' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                
                #### if Work Experience/Experience then Experience level
                elif 'EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'WORK EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'Work Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                else:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at Fresher level!!''',unsafe_allow_html=True)


                ## Skills Analyzing and Recommendation
                st.markdown('<h2 style="color:#2f8d46; font-weight:bold; margin-top:2em;">Skills Recommendation 💡</h2>', unsafe_allow_html=True)
                
                ### Current Analyzed Skills
                keywords = st_tags(label='### Your Current Skills',
                text='See our skills recommendation below',value=resume_data['skills'],key = '1  ')

                ### Keywords for Recommendations
                ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress','javascript', 'angular js', 'C#', 'Asp.net', 'flask']
                android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
                n_any = ['english','communication','writing', 'microsoft office', 'leadership','customer management', 'social media']
                ### Skill Recommendations Starts                
                recommended_skills = []
                reco_field = ''
                rec_course = ''

                ### condition starts to check skills from keywords and predict field
                for i in resume_data['skills']:
                
                    #### Data science recommendation
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success("** Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '2')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(ds_course)
                        break

                    #### Web development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success("** Our analysis says you are looking for Web Development Jobs **")
                        recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '3')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(web_course)
                        break

                    #### Android App Development
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success("** Our analysis says you are looking for Android App Development Jobs **")
                        recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '4')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(android_course)
                        break

                    #### IOS App Development
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                        recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '5')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(ios_course)
                        break

                    #### Ui-UX Recommendation
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                        recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '6')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(uiux_course)
                        break

                    #### For Not Any Recommendations
                    elif i.lower() in n_any:
                        print(i.lower())
                        reco_field = 'NA'
                        st.warning("** Currently our tool only predicts and recommends for Data Science, Web, Android, IOS and UI/UX Development**")
                        recommended_skills = ['No Recommendations']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Currently No Recommendations',value=recommended_skills,key = '6')
                        st.markdown('''<h5 style='text-align: left; color: #092851;'>Maybe Available in Future Updates</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = "Sorry! Not Available for this Field"
                        break


                ## Resume Scorer & Resume Writing Tips
                st.markdown('<h2 style="color:#2f8d46; font-weight:bold; margin-top:2em;">Resume Tips & Ideas 🥂</h2>', unsafe_allow_html=True)
                resume_score = 0
                
                ### Predicting Whether these key points are added to the resume
                if 'Objective' or 'Summary' in resume_text:
                    resume_score = resume_score+6
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added Objective/Summary</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="background:#d73b5c; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">❌ [-] Please add your career objective, it will give your career intension to the Recruiters.</div>', unsafe_allow_html=True)

                if 'Education' or 'School' or 'College'  in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added Education Details</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="background:#d73b5c; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">❌ [-] Please add Education. It will give Your Qualification level to the recruiter</div>', unsafe_allow_html=True)

                if 'EXPERIENCE' in resume_text:
                    resume_score = resume_score + 16
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added Experience</div>', unsafe_allow_html=True)
                elif 'Experience' in resume_text:
                    resume_score = resume_score + 16
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added Experience</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="background:#d73b5c; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">❌ [-] Please add Experience. It will help you to stand out from crowd</div>', unsafe_allow_html=True)

                if 'INTERNSHIPS'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added Internships</div>', unsafe_allow_html=True)
                elif 'INTERNSHIP'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added Internships</div>', unsafe_allow_html=True)
                elif 'Internships'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added Internships</div>', unsafe_allow_html=True)
                elif 'Internship'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added Internships</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="background:#d73b5c; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">❌ [-] Please add Internships. It will help you to stand out from crowd</div>', unsafe_allow_html=True)

                if 'SKILLS'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added Skills</div>', unsafe_allow_html=True)
                elif 'SKILL'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added Skills</div>', unsafe_allow_html=True)
                elif 'Skills'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added Skills</div>', unsafe_allow_html=True)
                elif 'Skill'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added Skills</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="background:#d73b5c; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">❌ [-] Please add Skills. It will help you a lot</div>', unsafe_allow_html=True)

                if 'HOBBIES' in resume_text:
                    resume_score = resume_score + 4
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added your Hobbies</div>', unsafe_allow_html=True)
                elif 'Hobbies' in resume_text:
                    resume_score = resume_score + 4
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added your Hobbies</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="background:#d73b5c; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">❌ [-] Please add Hobbies. It will show your personality to the Recruiters and give the assurance that you are fit for this role or not.</div>', unsafe_allow_html=True)

                if 'INTERESTS'in resume_text:
                    resume_score = resume_score + 5
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added your Interest</div>', unsafe_allow_html=True)
                elif 'Interests'in resume_text:
                    resume_score = resume_score + 5
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added your Interest</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="background:#d73b5c; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">❌ [-] Please add Interest. It will show your interest other that job.</div>', unsafe_allow_html=True)

                if 'ACHIEVEMENTS' in resume_text:
                    resume_score = resume_score + 13
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added your Achievements </div>', unsafe_allow_html=True)
                elif 'Achievements' in resume_text:
                    resume_score = resume_score + 13
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added your Achievements </div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="background:#d73b5c; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">❌ [-] Please add Achievements. It will show that you are capable for the required position.</div>', unsafe_allow_html=True)

                if 'CERTIFICATIONS' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added your Certifications </div>', unsafe_allow_html=True)
                elif 'Certifications' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added your Certifications </div>', unsafe_allow_html=True)
                elif 'Certification' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added your Certifications </div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="background:#d73b5c; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">❌ [-] Please add Certifications. It will show that you have done some specialization for the required position.</div>', unsafe_allow_html=True)

                if 'PROJECTS' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added your Projects</div>', unsafe_allow_html=True)
                elif 'PROJECT' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added your Projects</div>', unsafe_allow_html=True)
                elif 'Projects' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added your Projects</div>', unsafe_allow_html=True)
                elif 'Project' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('<div style="background:#2f8d46; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">✔️ [+] Awesome! You have added your Projects</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="background:#d73b5c; color:#fff; font-weight:bold; border-radius:6px; padding:8px 16px; margin-bottom:8px; display:inline-block;">❌ [-] Please add Projects. It will show that you have done work related the required position or not.</div>', unsafe_allow_html=True)

                st.markdown('<h2 style="color:#2f8d46; font-weight:bold; margin-top:2em;">Resume Score 📝</h2>', unsafe_allow_html=True)
                
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )

                ### Score Bar
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score +=1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)

                ### Score
                st.markdown(f'<div style="color:#2f8d46; font-weight:bold;">Your Resume Writing Score: {score}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#222; font-weight:bold;">Note: This score is calculated based on the content that you have in your Resume.</div>', unsafe_allow_html=True)

                # print(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)


                ### Getting Current Date and Time
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)


                ## Calling insert_data to add all the data into user_data                
                insert_data(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)

                ## Recommending Resume Writing Video
                st.markdown('<h2 style="color:#2f8d46; font-weight:bold; margin-top:2em;">Bonus Video for Resume Writing Tips💡</h2>', unsafe_allow_html=True)
                resume_vid = random.choice(resume_videos)
                st.video(resume_vid)

                ## Recommending Interview Preparation Video
                st.markdown('<h2 style="color:#2f8d46; font-weight:bold; margin-top:2em;">Bonus Video for Interview Tips💡</h2>', unsafe_allow_html=True)
                interview_vid = random.choice(interview_videos)
                st.video(interview_vid)

                ## On Successful Result 
                st.balloons()

                # After resume analysis, save to Sheet1
                if resume_data:
                    resume_save_data = {
                        'Name': act_name,
                        'Mail': act_mail,
                        'Mobile Number': act_mob,
                        'Resume Name': resume_data.get('name'),
                        'Resume Email': resume_data.get('email'),
                        'Resume Degree': resume_data.get('degree'),
                        'Resume Pages': resume_data.get('no_of_pages'),
                        'Skills': resume_data.get('skills'),
                        # Add more fields as needed
                    }
                    try:
                        save_to_excel(resume_save_data, filename='User_Data.xlsx', sheet_name='Sheet1')
                        st.success('Resume data saved to Excel successfully!')
                    except PermissionError:
                        st.error('Could not save to Excel. Please close User_Data.xlsx if it is open and try again.')
                    except ModuleNotFoundError as e:
                        st.error(f"Missing dependency: {e}. Please install the required package and try again.")
                    except Exception as e:
                        st.error(f"Error saving data to Excel: {e}")

            else:
                st.error('Something went wrong while analyzing your resume.')                


    ###### CODE FOR FEEDBACK SIDE ######
    elif choice == 'Feedback':   
        
        # timestamp 
        ts = time.time()
        cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        timestamp = str(cur_date+'_'+cur_time)

        # Feedback Form
        with st.form("my_form"):
            st.write("Feedback form")            
            feed_name = st.text_input('Name')
            feed_email = st.text_input('Email')
            feed_score = st.slider('Rate Us From 1 - 5', 1, 5)
            comments = st.text_input('Comments')
            Timestamp = timestamp        
            submitted = st.form_submit_button("Submit")
            if submitted:
                ## Calling insertf_data to add dat into user feedback
                insertf_data(feed_name,feed_email,feed_score,comments,Timestamp)    
                ## Success Message 
                st.success("Thanks! Your Feedback was recorded.") 
                ## On Successful Submit
                st.balloons()    

                # After feedback submission, save to Sheet2
                feedback_save_data = {
                    'Name': feed_name,
                    'Email': feed_email,
                    'Score': feed_score,
                    'Comments': comments,
                    'Timestamp': Timestamp
                }
                try:
                    save_to_excel(feedback_save_data, filename='User_Data.xlsx', sheet_name='Sheet2')
                    st.success('Feedback saved to Excel successfully!')
                except PermissionError:
                    st.error('Could not save feedback to Excel. Please close User_Data.xlsx if it is open and try again.')
                except ModuleNotFoundError as e:
                    st.error(f"Missing dependency: {e}. Please install the required package and try again.")
                except Exception as e:
                    st.error(f"Error saving feedback to Excel: {e}")


        # query to fetch data from user feedback table
        # query = 'select * from user_feedback'        
        # plotfeed_data = pd.read_sql(query, connection)                        

        # In feedback section, use in-memory feedback list for analytics
        if user_feedback_list:
            df = pd.DataFrame(user_feedback_list)
            st.subheader("**Past User Rating's**")
            if not df.empty:
                labels = df['feed_score'].unique()
                values = df['feed_score'].value_counts()
                import plotly.express as px
                fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5", color_discrete_sequence=px.colors.sequential.Aggrnyl)
                st.plotly_chart(fig)
                st.subheader("**User Comment's**")
                st.dataframe(df[['feed_name', 'comments']])
        else:
            st.info("No feedback data available.")

    
    ###### CODE FOR ABOUT PAGE ######
    elif choice == 'About':   

        st.subheader("**About The Tool - AI RESUME ANALYZER**")

        st.markdown('''
        <p align='justify'>
            A tool which parses information from a resume using natural language processing and finds the keywords, cluster them onto sectors based on their keywords. And lastly show recommendations, predictions, analytics to the applicant based on keyword matching.
        </p>
        <p align="justify">
            <b>How to use it: -</b> <br/><br/>
            <b>Junaid -</b> <br/>
            In the Side Bar choose yourself as Junaid and fill the required fields and upload your resume in pdf format.<br/>
            Just sit back and relax our tool will do the magic on it's own.<br/><br/>
            <b>Feedback -</b> <br/>
            A place where user can suggest some feedback about the tool.<br/><br/>
            <b>Admin -</b> <br/>
            For login use <b>admin</b> as username and <b>admin@resume-analyzer</b> as password.<br/>
            It will load all the required stuffs and perform analysis.
        </p><br/><br/>
        <p align="justify">
            Built by 
            <a href="https://www.linkedin.com/in/mohammed-junaid-dob25042004/" style="text-decoration: underline; color: #2f8d46; font-weight:bold;">Mohammed Junaid</a>
        </p>
        ''',unsafe_allow_html=True)  


    ###### CODE FOR ADMIN SIDE (ADMIN) ######
    else:
        st.success('Welcome to Admin Side')

        #  Admin Login
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button('Login'):
            
            ## Credentials 
            if ad_user == 'admin' and ad_password == 'admin@resume-analyzer':
                
                ### Fetch miscellaneous data from user_data(table) and convert it into dataframe
                # cursor.execute('''SELECT ID, ip_add, resume_score, convert(Predicted_Field using utf8), convert(User_level using utf8), city, state, country from user_data''')
                # datanalys = cursor.fetchall()
                # plot_data = pd.DataFrame(datanalys, columns=['Idt', 'IP_add', 'resume_score', 'Predicted_Field', 'User_Level', 'City', 'State', 'Country'])
                
                # Use in-memory user_data_list for analytics
                import pandas as pd
                if user_data_list:
                    plot_data = pd.DataFrame(user_data_list)
                    # Mask sensitive fields for display
                    if 'Mail' in plot_data.columns:
                        plot_data['Mail'] = plot_data['Mail'].apply(mask_email)
                    if 'Mobile Number' in plot_data.columns:
                        plot_data['Mobile Number'] = plot_data['Mobile Number'].apply(mask_phone)
                    st.success("Welcome Junaid ! Total %d User's Have Used Our Tool : )" % len(plot_data))
                    st.header("**User's Data**")
                    page_size = 20
                    total_rows = len(plot_data)
                    if total_rows > page_size:
                        total_pages = (total_rows - 1) // page_size + 1
                        page = st.number_input('Page', min_value=1, max_value=total_pages, value=1, step=1)
                        start_idx = (page - 1) * page_size
                        end_idx = start_idx + page_size
                        st.dataframe(plot_data.iloc[start_idx:end_idx])
                        st.caption(f"Showing rows {start_idx+1} to {min(end_idx, total_rows)} of {total_rows}")
                    else:
                        st.dataframe(plot_data)
                else:
                    st.info("No user data available.")

                ### Fetch user data from user_data(table) and convert it into dataframe
                # cursor.execute('''SELECT ID, sec_token, ip_add, act_name, act_mail, act_mob, convert(Predicted_Field using utf8), Timestamp, Name, Email_ID, resume_score, Page_no, pdf_name, convert(User_level using utf8), convert(Actual_skills using utf8), convert(Recommended_skills using utf8), convert(Recommended_courses using utf8), city, state, country, latlong, os_name_ver, host_name, dev_user from user_data''')
                # data = cursor.fetchall()                

                # st.header("**User's Data**")
                # df = pd.DataFrame(data, columns=['ID', 'Token', 'IP Address', 'Name', 'Mail', 'Mobile Number', 'Predicted Field', 'Timestamp',
                #                                  'Predicted Name', 'Predicted Mail', 'Resume Score', 'Total Page',  'File Name',   
                #                                  'User Level', 'Actual Skills', 'Recommended Skills', 'Recommended Course',
                #                                  'City', 'State', 'Country', 'Lat Long', 'Server OS', 'Server Name', 'Server User',])
                
                ### Viewing the dataframe
                # st.dataframe(df)
                
                ### Downloading Report of user_data in csv file
                # st.markdown(get_csv_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)

                ### Fetch feedback data from user_feedback(table) and convert it into dataframe
                # cursor.execute('''SELECT * from user_feedback''')
                # data = cursor.fetchall()

                # st.header("**User's Feedback Data**")
                # df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Feedback Score', 'Comments', 'Timestamp'])
                # st.dataframe(df)

                ### query to fetch data from user_feedback(table)
                # query = 'select * from user_feedback'
                # plotfeed_data = pd.read_sql(query, connection)                        

                ### Analyzing All the Data's in pie charts

                # fetching feed_score from the query and getting the unique values and total value count 
                # labels = plotfeed_data.feed_score.unique()
                # values = plotfeed_data.feed_score.value_counts()
                
                # Pie chart for user ratings
                # st.subheader("**User Rating's**")
                # fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5 🤗", color_discrete_sequence=px.colors.sequential.Aggrnyl)
                # st.plotly_chart(fig)

                # fetching Predicted_Field from the query and getting the unique values and total value count                 
                # labels = plot_data.Predicted_Field.unique()
                # values = plot_data.Predicted_Field.value_counts()

                # Pie chart for predicted field recommendations
                # st.subheader("**Pie-Chart for Predicted Field Recommendation**")
                # fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills 👽', color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
                # st.plotly_chart(fig)

                # fetching User_Level from the query and getting the unique values and total value count                 
                # labels = plot_data.User_Level.unique()
                # values = plot_data.User_Level.value_counts()

                # Pie chart for User's👨‍💻 Experienced Level
                # st.subheader("**Pie-Chart for User's Experienced Level**")
                # fig = px.pie(df, values=values, names=labels, title="Pie-Chart 📈 for User's 👨‍💻 Experienced Level", color_discrete_sequence=px.colors.sequential.RdBu)
                # st.plotly_chart(fig)

                # fetching resume_score from the query and getting the unique values and total value count                 
                # labels = plot_data.resume_score.unique()                
                # values = plot_data.resume_score.value_counts()

                # Pie chart for Resume Score
                # st.subheader("**Pie-Chart for Resume Score**")
                # fig = px.pie(df, values=values, names=labels, title='From 1 to 100 💯', color_discrete_sequence=px.colors.sequential.Agsunset)
                # st.plotly_chart(fig)

                # fetching IP_add from the query and getting the unique values and total value count 
                # labels = plot_data.IP_add.unique()
                # values = plot_data.IP_add.value_counts()

                # Pie chart for Users
                # st.subheader("**Pie-Chart for Users App Used Count**")
                # fig = px.pie(df, values=values, names=labels, title='Usage Based On IP Address 👥', color_discrete_sequence=px.colors.sequential.matter_r)
                # st.plotly_chart(fig)

                # fetching City from the query and getting the unique values and total value count 
                # labels = plot_data.City.unique()
                # values = plot_data.City.value_counts()

                # Pie chart for City
                # st.subheader("**Pie-Chart for City**")
                # fig = px.pie(df, values=values, names=labels, title='Usage Based On City 🌆', color_discrete_sequence=px.colors.sequential.Jet)
                # st.plotly_chart(fig)

                # fetching State from the query and getting the unique values and total value count 
                # labels = plot_data.State.unique()
                # values = plot_data.State.value_counts()

                # Pie chart for State
                # st.subheader("**Pie-Chart for State**")
                # fig = px.pie(df, values=values, names=labels, title='Usage Based on State 🚉', color_discrete_sequence=px.colors.sequential.PuBu_r)
                # st.plotly_chart(fig)

                # fetching Country from the query and getting the unique values and total value count 
                # labels = plot_data.Country.unique()
                # values = plot_data.Country.value_counts()

                # Pie chart for Country
                # st.subheader("**Pie-Chart for Country**")
                # fig = px.pie(df, values=values, names=labels, title='Usage Based on Country 🌏', color_discrete_sequence=px.colors.sequential.Purpor_r)
                # st.plotly_chart(fig)

            ## For Wrong Credentials
            else:
                st.error("Wrong ID & Password Provided")

# Calling the main (run()) function to make the whole process run
run()
