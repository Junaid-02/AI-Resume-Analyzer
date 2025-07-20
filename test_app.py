import pandas as pd
import os
from App.App import save_to_excel

def test_save_resume():
    resume_data = {
        'Name': 'Test User',
        'Mail': 'testuser@example.com',
        'Mobile Number': '9876543210',
        'Resume Name': 'Test User',
        'Resume Email': 'testuser@example.com',
        'Resume Degree': 'B.Tech',
        'Resume Pages': 2,
        'Skills': ['Python', 'Data Science']
    }
    save_to_excel(resume_data, filename='User_Data.xlsx', sheet_name='Sheet1')
    df = pd.read_excel('User_Data.xlsx', sheet_name='Sheet1')
    assert (df['Mail'] == 'testuser@example.com').any(), 'Resume data not saved!'
    print('Resume data saved and verified in Sheet1.')

def test_save_feedback():
    feedback_data = {
        'Name': 'Test User',
        'Email': 'testuser@example.com',
        'Score': 5,
        'Comments': 'Great tool!',
        'Timestamp': '2024-07-20_12:00:00'
    }
    save_to_excel(feedback_data, filename='User_Data.xlsx', sheet_name='Sheet2')
    df = pd.read_excel('User_Data.xlsx', sheet_name='Sheet2')
    assert (df['Email'] == 'testuser@example.com').any(), 'Feedback data not saved!'
    print('Feedback data saved and verified in Sheet2.')

if __name__ == '__main__':
    test_save_resume()
    test_save_feedback()
    print('All tests passed!') 