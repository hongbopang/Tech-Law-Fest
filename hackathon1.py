# Flask stuff
from flask import Flask, render_template, jsonify, request, Markup
# for read google spreadsheet
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from decimal import Decimal
from operator import add

# initiate flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'WHYDOINEEDTHIS!'

# add everything

# This function returns the number of each entries
def find_breakdown(variable_data, opt_positive, opt_negative, opt_neg1 = 'dkfhakjfsnbkjfhb', opt_neg2='kdjhfksnsjfgf'):
    result=[]
    num_1=variable_data.count(opt_positive)
    num_2=variable_data.count(opt_negative)+variable_data.count(opt_neg1)+variable_data.count(opt_neg2)
    result.append(num_1)
    result.append(num_2)
    result.append(num_1/(num_1+num_2)*100)
    return result

def find_breakdown_minor(variable_data, opt_positive, opt_negative, opt_neg1 = 'dkfhakjfsnbkjfhb', opt_neg2='kdjhfksnsjfgf'):
    result=[]
    num_1=variable_data.count(opt_positive)
    num_2=variable_data.count(opt_negative)+variable_data.count(opt_neg1)+variable_data.count(opt_neg2)
    result.append(num_1)
    result.append(num_2)
    return result


# returns index values of all that has the values
def find_all(data_variable,condition):
    answer = [i for i, x in enumerate(data_variable) if x == condition]
    return answer

def find_not(data_variable,condition):
    answer = [i for i, x in enumerate(data_variable) if x != condition]
    return answer

def zigzag(list):
    return list[::2], list[1::2]

def last_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))  # fastest
    return str(len(str_list))

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

#define countrylist here
country_list=[0,0,'Singapore','Hong Kong','India','Philippines','Malaysia','EU']

#render the main pages
@app.route('/')
def home():
    return render_template('main_home.html')

@app.route('/main_assess/')
def main_assess():
    return render_template("main_assess.html")

@app.route('/main_comparison/')
def main_comparison():
    return render_template("main_comparison.html")

@app.route('/main_analysis/')
def main_analysis():
    Entry_1='Yes'
    Entry_2='No'
    protection_answer_sheet = client.open("Protection Obligation Data").sheet1
    row_num=last_row(protection_answer_sheet)
    protection_answers=protection_answer_sheet.row_values(row_num)
    protection_breakdown=find_breakdown_minor(protection_answers, Entry_1, Entry_2)

    access_answer_sheet = client.open("Access Obligation Data").sheet1
    row_num=last_row(access_answer_sheet)
    access_total=access_answer_sheet.row_values(row_num)
    access_answer=access_total[0:5]
    openness_answer=access_total[5:12]
    accuracy_answer=access_total[12]
    access_breakdown=find_breakdown_minor(access_answer, Entry_1, Entry_2)
    openness_breakdown=find_breakdown_minor(openness_answer, Entry_1, Entry_2)
    accuracy_breakdown=find_breakdown_minor(accuracy_answer, Entry_1, Entry_2)

    consent_answer_sheet = client.open("Consent Obligation Data").sheet1
    row_num=last_row(consent_answer_sheet)
    consent_total=consent_answer_sheet.row_values(row_num)
    consent_answer=consent_total[0:2]
    notification_answer=consent_total[2:7]
    notification_answer.append(consent_total[10])
    purpose_answer=consent_total[7:10]
    consent_breakdown=find_breakdown_minor(consent_answer, Entry_1, Entry_2)
    notification_breakdown=find_breakdown_minor(notification_answer, Entry_1, Entry_2)
    purpose_breakdown=find_breakdown_minor(purpose_answer, Entry_1, Entry_2)

    transfer_answer_sheet = client.open("Transfer Obligation Data").sheet1
    row_num=last_row(transfer_answer_sheet)
    transfer_total=transfer_answer_sheet.row_values(row_num)
    transfer_answer=transfer_total[0:5]
    retention_answer=transfer_total[5:8]
    transfer_breakdown=find_breakdown_minor(transfer_answer, Entry_1, Entry_2)
    retention_breakdown=find_breakdown_minor(retention_answer, Entry_1, Entry_2)

    labels = ["Compliant","Non-Compliant"]
    colors = [ "#008000", "#ff0000"]

    total_result=[]
    for x in range(len(protection_breakdown)):
        total_result.append(protection_breakdown[x]+access_breakdown[x]+openness_breakdown[x]+accuracy_breakdown[x]+consent_breakdown[x]+notification_breakdown[x]+purpose_breakdown[x]+transfer_breakdown[x]+retention_breakdown[x])

    total_compliance=(round((total_result[0]/(total_result[0]+total_result[1]))*100,0))

    return render_template("main_analysis.html",protection_breakdown=protection_breakdown,access_breakdown=access_breakdown,openness_breakdown=openness_breakdown,accuracy_breakdown=accuracy_breakdown,consent_breakdown=consent_breakdown, \
    notification_breakdown=notification_breakdown,purpose_breakdown=purpose_breakdown,transfer_breakdown=transfer_breakdown,retention_breakdown=retention_breakdown,total_result=total_result, \
    protection_graph=zip(protection_breakdown, labels, colors), accuracy_graph=zip(accuracy_breakdown, labels, colors), access_graph=zip(access_breakdown, labels, colors), openness_graph=zip(openness_breakdown, labels, colors), \
    notification_graph=zip(notification_breakdown, labels, colors), consent_graph=zip(consent_breakdown, labels, colors), purpose_graph=zip(purpose_breakdown, labels, colors), retention_graph=zip(retention_breakdown, labels, colors), \
    transfer_graph=zip(transfer_breakdown, labels, colors), main_graph=zip(total_result, labels, colors),total_compliance=total_compliance)

@app.route('/comparison_result/')
def comparison_result():
    #uniersal stuff
    comparison_data=client.open("Comparison Data").sheet1 #this is the data from the tyepform
    comparison_lookup=client.open("Base Data").sheet1 #this is the reference sheet

    row_number=last_row(comparison_data) #this calls the final row

    # calling two countries
    country_1=comparison_data.cell(row_number, 1).value
    country_2=comparison_data.cell(row_number, 2).value #this calls the two countries from the survey
    countries=[country_1, country_2] #this just wraps the two countries into a single list
    country_1_index=country_list.index(country_1)
    country_2_index=country_list.index(country_2) #this calls the countries into index form
    countries_index=[]
    countries_index.append(country_1_index)
    countries_index.append(country_2_index) #this converts the index into a list

    #### Personal
    Personal_data_key = [] #dummy to store to indexs

    Personal_data_rows =(3,4,5) #this is hardocded please refer to spreadsheet for the numbers
    for i in Personal_data_rows:
        Personal_data_key.append(comparison_lookup.cell(i,1).value) #generate as a list the original data

    Personal_data_CSV=comparison_data.cell(row_number, 4).value #this calls the survey result answers
    Personal_data_answers=Personal_data_CSV.split(', ')   #transfers the called data into a list seperated by ', '. need the space because the system generates the space we are check with identical

    personal_index=[i for i, x in enumerate(Personal_data_key) if any(thing in x for thing in Personal_data_answers)] #checks for index that are replicates
    personal_index=[x+3 for x in personal_index] #offsets so that indexs match

    ### to find personal, use as a template ###
    personal_to_print=[]
    indices_to_print=[]
    for k in countries_index:
        for j in personal_index:
            indices_to_print.append([j,k]) #adds a pair of locations to help find the value later one

    for llama in indices_to_print:
        personal_to_print.append(comparison_lookup.cell(llama[0],llama[1]).value) #generates the list of data to display

    personal_1 = personal_to_print[0:3]
    personal_2 = personal_to_print[3:6]

    #### sensitive
    Sensitive_data_CSV=comparison_data.cell(row_number, 5).value
    Sensitive_data_answers=Sensitive_data_CSV.split(', ')
    Sensitive_data_key = []
    Sensitive_data_rows=(7,8,9,10,11,12,13)

    for i in Sensitive_data_rows:
        Sensitive_data_key.append(comparison_lookup.cell(i,1).value)

    sensitive_index=[i for i, x in enumerate(Sensitive_data_key) if any(thing in x for thing in Sensitive_data_answers)]
    sensitive_index=[x+7 for x in sensitive_index]
    sensitive_to_print=[]

### to find sensitive, use as a template ###
    indices_to_print=[]
    for k in countries_index:
        for j in sensitive_index:
            indices_to_print.append([j,k])

    for llama in indices_to_print:
        sensitive_to_print.append(comparison_lookup.cell(llama[0],llama[1]).value)

    sensitive_1 = sensitive_to_print[0:7]
    sensitive_2 = sensitive_to_print[7:14]

    Sensitive_data_answers = ['Financial data', 'Medical information', 'Personal identifier', 'Biometric information', 'Personal history', 'Insurance information', 'Minors information']


### to find sensitive, use as a template ###
    return render_template("comparison_result.html",personal_1=personal_1,personal_2=personal_2,Personal_data_answers=Personal_data_answers,countries=countries,sensitive_1=sensitive_1,sensitive_2=sensitive_2,Sensitive_data_answers=Sensitive_data_answers)

# render assess pages
@app.route('/assess_protection/')
def assess_protection():
    return render_template("assess_protection.html")

@app.route('/assess_access/')
def assess_access():
    return render_template("assess_access.html")

@app.route('/assess_consent/')
def assess_consent():
    return render_template("assess_consent.html")

@app.route('/assess_transfer/')
def assess_transfer():
    return render_template("assess_transfer.html")

# render result pages
@app.route("/results_protection")
def results_protection():
    # call the googlesheet
    obligation_answers = client.open("Protection Obligation Data").sheet1
    obligation_worksheet = client.open("Base Data")
    protection_spreadsheet=obligation_worksheet.get_worksheet(1)

    row_num=last_row(obligation_answers)
    test1_answers=obligation_answers.row_values(row_num)

    Entry_1="Yes"
    Entry_2="No"

    test1_result=find_breakdown(test1_answers, Entry_1, Entry_2)
    percent_overall_protection=test1_result.pop()
    percent_overall_protection=round(percent_overall_protection,0)
    labels = ["Compliant","Non-Compliant"]
    values = test1_result
    colors = [ "#008000", "#ff0000"]

    test1_answers=obligation_answers.row_values(row_num)
    rec_index=find_all(test1_answers,'No')
    rec_index=[x+1 for x in rec_index]

    test1_obligation=protection_spreadsheet.col_values(9)
    test1_fine=protection_spreadsheet.col_values(7)
    test1_quest=protection_spreadsheet.col_values(1)
    test1_rec=[test1_obligation[i] for i in rec_index]
    test1_monetary=[test1_fine[i] for i in rec_index]
    test1_monetary=list(map(int, test1_monetary))
    total_liability=sum(test1_monetary)
    test1_qns=[test1_quest[i] for i in rec_index]

    money_index=find_not(test1_monetary,0)
    test1_lia=[test1_monetary[i] for i in money_index]

    test1_precedent=protection_spreadsheet.col_values(10)
    test1_law=[test1_precedent[i] for i in rec_index]
    test1_moneylia=[test1_law[i] for i in money_index]
    return render_template('results_protection.html',test1_moneylia=test1_moneylia, test1_lia=test1_lia,test1_law=test1_law, rec_index=rec_index,set=zip(values, labels, colors),percent_overall_protection=percent_overall_protection,test1_rec=test1_rec, test1_monetary=test1_monetary, total_liability=total_liability,test1_qns=test1_qns)

@app.route("/results_access/")
def results_access():
    obligation_answers = client.open("Access Obligation Data").sheet1
    obligation_worksheet = client.open("Base Data")
    protection_spreadsheet=obligation_worksheet.get_worksheet(2)

    row_num=last_row(obligation_answers)
    test1_answers=obligation_answers.row_values(row_num)
    test1_answers=test1_answers[0:5] #row value is hardcoded

    Entry_1="Yes"
    Entry_2="No"

    test1_result=find_breakdown(test1_answers, Entry_1, Entry_2)

    percent_overall_protection=test1_result.pop()
    percent_overall_protection=round(percent_overall_protection,0)

    labels = ["Compliant","Non-Compliant"]
    values = test1_result
    colors = [ "#008000", "#ff0000"]

    rec_index=find_all(test1_answers,'No')
    rec_index=[x+1 for x in rec_index]
    test1_obligation=protection_spreadsheet.col_values(9)
    test1_fine=protection_spreadsheet.col_values(7)
    test1_quest=protection_spreadsheet.col_values(1)
    test1_rec=[test1_obligation[i] for i in rec_index]
    test1_monetary=[test1_fine[i] for i in rec_index]
    test1_monetary=list(map(int, test1_monetary))
    total_liability=sum(test1_monetary)
    test1_qns=[test1_quest[i] for i in rec_index]

    money_index=find_not(test1_monetary,0)
    test1_lia=[test1_monetary[i] for i in money_index]

    test1_precedent=protection_spreadsheet.col_values(10)
    test1_law=[test1_precedent[i] for i in rec_index]
    test1_moneylia=[test1_law[i] for i in money_index]
    return render_template('results_access.html',test1_moneylia=test1_moneylia, test1_lia=test1_lia,test1_law=test1_law, rec_index=rec_index,set=zip(values, labels, colors),percent_overall_protection=percent_overall_protection,test1_rec=test1_rec, test1_monetary=test1_monetary, total_liability=total_liability,test1_qns=test1_qns)

@app.route("/results_accuracy")
def results_accuracy():
    obligation_answers = client.open("Access Obligation Data").sheet1
    obligation_worksheet = client.open("Base Data")
    protection_spreadsheet=obligation_worksheet.get_worksheet(2)

    row_num=last_row(obligation_answers)
    test1_answers=obligation_answers.row_values(row_num)

    test1_answers[0:12]='123456789012' #hardcoded

    Entry_1="Yes"
    Entry_2="No"

    test1_result=find_breakdown(test1_answers, Entry_1, Entry_2)
    percent_overall_protection=test1_result.pop()
    percent_overall_protection=round(percent_overall_protection,0)

    labels = ["Compliant","Non-Compliant"]
    values = test1_result
    colors = [ "#008000", "#ff0000"]

    rec_index=find_all(test1_answers,'No')
    rec_index=[x+1 for x in rec_index]

    test1_obligation=protection_spreadsheet.col_values(9)
    test1_fine=protection_spreadsheet.col_values(7)
    test1_quest=protection_spreadsheet.col_values(1)
    test1_rec=[test1_obligation[i] for i in rec_index]
    test1_monetary=[test1_fine[i] for i in rec_index]
    test1_monetary=list(map(int, test1_monetary))
    total_liability=sum(test1_monetary)
    test1_qns=[test1_quest[i] for i in rec_index]

    money_index=find_not(test1_monetary,0)
    test1_lia=[test1_monetary[i] for i in money_index]

    test1_precedent=protection_spreadsheet.col_values(10)
    test1_law=[test1_precedent[i] for i in rec_index]
    test1_moneylia=[test1_law[i] for i in money_index]
    return render_template('results_accuracy.html',test1_moneylia=test1_moneylia, test1_lia=test1_lia,test1_law=test1_law, rec_index=rec_index,set=zip(values, labels, colors),percent_overall_protection=percent_overall_protection,test1_rec=test1_rec, test1_monetary=test1_monetary, total_liability=total_liability,test1_qns=test1_qns)

@app.route('/results_openness/')
def results_openness():
    obligation_answers = client.open("Access Obligation Data").sheet1
    obligation_worksheet = client.open("Base Data")
    protection_spreadsheet=obligation_worksheet.get_worksheet(2)

    row_num=last_row(obligation_answers)
    test1_answers=obligation_answers.row_values(row_num)

    test1_answers[0:5]='01234' #hardcoded
    test1_answers[12]='2'

    Entry_1="Yes"
    Entry_2="No"

    test1_result=find_breakdown(test1_answers, Entry_1, Entry_2)
    percent_overall_protection=test1_result.pop()
    percent_overall_protection=round(percent_overall_protection,0)

    labels = ["Compliant","Non-Compliant"]
    values = test1_result
    colors = [ "#008000", "#ff0000"]

    rec_index=find_all(test1_answers,'No')
    rec_index=[x+1 for x in rec_index]

    test1_obligation=protection_spreadsheet.col_values(9)
    test1_fine=protection_spreadsheet.col_values(7)
    test1_quest=protection_spreadsheet.col_values(1)
    test1_rec=[test1_obligation[i] for i in rec_index]
    test1_monetary=[test1_fine[i] for i in rec_index]
    test1_monetary=list(map(int, test1_monetary))
    total_liability=sum(test1_monetary)
    test1_qns=[test1_quest[i] for i in rec_index]

    money_index=find_not(test1_monetary,0)
    test1_lia=[test1_monetary[i] for i in money_index]

    test1_precedent=protection_spreadsheet.col_values(10)
    test1_law=[test1_precedent[i] for i in rec_index]
    test1_moneylia=[test1_law[i] for i in money_index]
    return render_template('results_openness.html', test1_moneylia=test1_moneylia, test1_lia=test1_lia, test1_law=test1_law, rec_index=rec_index,set=zip(values, labels, colors),percent_overall_protection=percent_overall_protection,test1_rec=test1_rec, test1_monetary=test1_monetary, total_liability=total_liability,test1_qns=test1_qns)

@app.route("/results_consent")
def results_consent():
    obligation_answers = client.open("Consent Obligation Data").sheet1
    obligation_worksheet = client.open("Base Data")
    protection_spreadsheet=obligation_worksheet.get_worksheet(3)

    row_num=last_row(obligation_answers)
    test1_answers=obligation_answers.row_values(row_num)
    test1_answers=test1_answers[0:2] #hardcoded

    Entry_1="Yes"
    Entry_2="No"

    test1_result=find_breakdown(test1_answers, Entry_1, Entry_2)
    percent_overall_protection=test1_result.pop()
    percent_overall_protection=round(percent_overall_protection,0)

    labels = ["Compliant","Non-Compliant"]
    values = test1_result
    colors = [ "#008000", "#ff0000"]

    rec_index=find_all(test1_answers,'No')
    rec_index=[x+1 for x in rec_index]

    test1_obligation=protection_spreadsheet.col_values(9)
    test1_fine=protection_spreadsheet.col_values(7)
    test1_quest=protection_spreadsheet.col_values(1)
    test1_rec=[test1_obligation[i] for i in rec_index]
    test1_monetary=[test1_fine[i] for i in rec_index]
    test1_monetary=list(map(int, test1_monetary))
    total_liability=sum(test1_monetary)
    test1_qns=[test1_quest[i] for i in rec_index]

    money_index=find_not(test1_monetary,0)
    test1_lia=[test1_monetary[i] for i in money_index]

    test1_precedent=protection_spreadsheet.col_values(10)
    test1_law=[test1_precedent[i] for i in rec_index]
    test1_moneylia=[test1_law[i] for i in money_index]
    return render_template('results_consent.html', test1_moneylia=test1_moneylia, test1_lia=test1_lia,test1_law=test1_law, rec_index=rec_index,set=zip(values, labels, colors),percent_overall_protection=percent_overall_protection,test1_rec=test1_rec, test1_monetary=test1_monetary, total_liability=total_liability,test1_qns=test1_qns)

@app.route('/results_notification/')
def results_notification():
    obligation_answers = client.open("Consent Obligation Data").sheet1
    obligation_worksheet = client.open("Base Data")
    protection_spreadsheet=obligation_worksheet.get_worksheet(3)

    row_num=last_row(obligation_answers)
    test1_answers=obligation_answers.row_values(row_num)
    test1_answers[0:2]='012'
    test1_answers[8:11]='890' #hardcoded

    Entry_1="Yes"
    Entry_2="No"

    test1_result=find_breakdown(test1_answers, Entry_1, Entry_2)
    percent_overall_protection=test1_result.pop()
    percent_overall_protection=round(percent_overall_protection,0)

    labels = ["Compliant","Non-Compliant"]
    values = test1_result
    colors = [ "#008000", "#ff0000"]

    rec_index=find_all(test1_answers,'No')

    test1_obligation=protection_spreadsheet.col_values(9)

    test1_fine=protection_spreadsheet.col_values(7)
    test1_quest=protection_spreadsheet.col_values(1)
    test1_rec=[test1_obligation[i] for i in rec_index]
    test1_monetary=[test1_fine[i] for i in rec_index]
    test1_monetary=list(map(int, test1_monetary))
    total_liability=sum(test1_monetary)
    test1_qns=[test1_quest[i] for i in rec_index]

    money_index=find_not(test1_monetary,0)
    test1_lia=[test1_monetary[i] for i in money_index]

    test1_precedent=protection_spreadsheet.col_values(10)
    test1_law=[test1_precedent[i] for i in rec_index]
    test1_moneylia=[test1_law[i] for i in money_index]
    return render_template('results_notification.html', test1_moneylia=test1_moneylia, test1_lia=test1_lia,test1_law=test1_law,rec_index=rec_index,set=zip(values, labels, colors),percent_overall_protection=percent_overall_protection,test1_rec=test1_rec, test1_monetary=test1_monetary, total_liability=total_liability,test1_qns=test1_qns)

@app.route('/results_purpose/')
def results_purpose():
    obligation_answers = client.open("Consent Obligation Data").sheet1
    obligation_worksheet = client.open("Base Data")
    protection_spreadsheet=obligation_worksheet.get_worksheet(3)

    row_num=last_row(obligation_answers)
    test1_answers=obligation_answers.row_values(row_num)
    test1_answers[0:9]='01234567' #hardcoded
    test1_answers[11]='1'

    Entry_1="Yes"
    Entry_2="No"

    test1_result=find_breakdown(test1_answers, Entry_1, Entry_2)
    percent_overall_protection=test1_result.pop()
    percent_overall_protection=round(percent_overall_protection,0)

    labels = ["Compliant","Non-Compliant"]
    values = test1_result
    colors = [ "#008000", "#ff0000"]

    rec_index=find_all(test1_answers,'No')
    rec_index=[x-1 for x in rec_index]

    test1_obligation=protection_spreadsheet.col_values(9)
    test1_fine=protection_spreadsheet.col_values(7)
    test1_quest=protection_spreadsheet.col_values(1)
    test1_rec=[test1_obligation[i] for i in rec_index]
    test1_monetary=[test1_fine[i] for i in rec_index]
    test1_monetary=list(map(int, test1_monetary))
    total_liability=sum(test1_monetary)
    test1_qns=[test1_quest[i] for i in rec_index]

    money_index=find_not(test1_monetary,0)
    test1_lia=[test1_monetary[i] for i in money_index]

    test1_precedent=protection_spreadsheet.col_values(10)
    test1_law=[test1_precedent[i] for i in rec_index]
    test1_moneylia=[test1_law[i] for i in money_index]
    return render_template('results_purpose.html', test1_moneylia=test1_moneylia, test1_lia=test1_lia,test1_law=test1_law, rec_index=rec_index,set=zip(values, labels, colors),percent_overall_protection=percent_overall_protection,test1_rec=test1_rec, test1_monetary=test1_monetary, total_liability=total_liability,test1_qns=test1_qns)

@app.route("/results_transfer")
def results_transfer():
    obligation_answers = client.open("Transfer Obligation Data").sheet1
    obligation_worksheet = client.open("Base Data")
    protection_spreadsheet=obligation_worksheet.get_worksheet(4)

    row_num=last_row(obligation_answers)
    test1_answers=obligation_answers.row_values(row_num)
    test1_answers[0:5]='01234' #hardcoded

    Entry_1="Yes"
    Entry_2="No"

    test1_result=find_breakdown(test1_answers, Entry_1, Entry_2)
    percent_overall_protection=test1_result.pop()
    percent_overall_protection=round(percent_overall_protection,0)

    labels = ["Compliant","Non-Compliant"]
    values = test1_result
    colors = [ "#008000", "#ff0000"]

    rec_index=find_all(test1_answers,'No')
    rec_index=[x+1 for x in rec_index]

    test1_obligation=protection_spreadsheet.col_values(9)
    test1_fine=protection_spreadsheet.col_values(7)
    test1_quest=protection_spreadsheet.col_values(1)
    test1_rec=[test1_obligation[i] for i in rec_index]
    test1_monetary=[test1_fine[i] for i in rec_index]
    test1_monetary=list(map(int, test1_monetary))
    total_liability=sum(test1_monetary)
    test1_qns=[test1_quest[i] for i in rec_index]

    money_index=find_not(test1_monetary,0)
    test1_lia=[test1_monetary[i] for i in money_index]

    test1_precedent=protection_spreadsheet.col_values(10)
    test1_law=[test1_precedent[i] for i in rec_index]
    test1_moneylia=[test1_law[i] for i in money_index]
    return render_template('results_transfer.html', test1_moneylia=test1_moneylia, test1_lia=test1_lia,test1_law=test1_law,rec_index=rec_index,set=zip(values, labels, colors),percent_overall_protection=percent_overall_protection,test1_rec=test1_rec, test1_monetary=test1_monetary, total_liability=total_liability,test1_qns=test1_qns)

@app.route('/results_retention/')
def results_retention():
    obligation_answers = client.open("Transfer Obligation Data").sheet1
    obligation_worksheet = client.open("Base Data")
    protection_spreadsheet=obligation_worksheet.get_worksheet(4)

    row_num=last_row(obligation_answers)
    test1_answers=obligation_answers.row_values(row_num)
    test1_answers=test1_answers[0:5]

    Entry_1="Yes"
    Entry_2="No"

    test1_result=find_breakdown(test1_answers, Entry_1, Entry_2)
    percent_overall_protection=test1_result.pop()
    percent_overall_protection=round(percent_overall_protection,0)

    labels = ["Compliant","Non-Compliant"]
    values = test1_result
    colors = [ "#008000", "#ff0000"]

    rec_index=find_all(test1_answers,'No')
    rec_index=[x+1 for x in rec_index]

    test1_obligation=protection_spreadsheet.col_values(9)
    test1_fine=protection_spreadsheet.col_values(7)
    test1_quest=protection_spreadsheet.col_values(1)
    test1_rec=[test1_obligation[i] for i in rec_index]
    test1_monetary=[test1_fine[i] for i in rec_index]
    test1_monetary=list(map(int, test1_monetary))
    total_liability=sum(test1_monetary)
    test1_qns=[test1_quest[i] for i in rec_index]

    money_index=find_not(test1_monetary,0)
    test1_lia=[test1_monetary[i] for i in money_index]

    test1_precedent=protection_spreadsheet.col_values(10)
    test1_law=[test1_precedent[i] for i in rec_index]
    test1_moneylia=[test1_law[i] for i in money_index]
    return render_template('results_retention.html',test1_moneylia=test1_moneylia, test1_lia=test1_lia, test1_law=test1_law,set=zip(values, labels, colors),rec_index=rec_index,data=values,percent_overall_protection=percent_overall_protection,test1_rec=test1_rec, test1_monetary=test1_monetary, total_liability=total_liability,test1_qns=test1_qns)

if __name__=="__main__":
    app.run(debug=True)
