from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
import os
import shutil

import os 

def vk(v, index):
    if index in v:
        return v[index]
    return {
        'y': 0,
        'tree': []
        }

def meyer(a,b):
    m=len(a)
    n=len(b)
    v={}
    for d in range(m+n+1):
        for k in range(-d,d+1,2):
            if k<-n or k>m:
                continue                
            current_vk=vk(v,str(k))
            next_vk=None
            prev_vk=None
            if d!=0:
                can_move_prev_vk=False
                next_vk=vk(v,str(k+1))
                prev_vk=vk(v,str(k-1))
                if k==-d or k==-n:
                    can_move_prev_vk=False
                elif k==d or k==m:
                    can_move_prev_vk=True
                else:
                    if prev_vk["y"]>next_vk["y"]:
                        can_move_prev_vk=True
                    else:
                        can_move_prev_vk=False

                if can_move_prev_vk:
                    current_vk["y"]=prev_vk["y"]
                    current_vk['tree']=list(prev_vk['tree'])
                    current_vk['tree'].append(-1)
                else:
                    current_vk['y']=next_vk['y'] + 1
                    current_vk['tree']=list(next_vk['tree'])
                    current_vk['tree'].append(1)
            y=current_vk['y']
            x=k+y
            while x<m and y<n and a[x]==b[y]:
                current_vk['tree'].append(0)
                x=x+1
                y=y+1
            current_vk['y']=y
            if x >= m and y>=n:
                return current_vk['tree']
            v[str(k)]=current_vk
            
def mayer_ses(a,b):
    a_ses=[]
    b_ses=[]
    diffclass=False
    actions=meyer(a,b)
    a_index=0
    b_index=0
    for action in actions:
        if action==0:
            a_ses.append(a[a_index])
            b_ses.append(a[a_index])
            a_index+=1
            b_index+=1
        elif action==1:
            b_ses.append("+"+b[b_index])
            b_index+=1
            diffclass=True
        else:
            a_ses.append("-"+a[a_index])
            a_index+=1
            diffclass=True
    return a_ses,b_ses,diffclass


login_username="####"
login_password="####"

slack_url="####"
pass_oldcontent="oldcontent.txt"
pass_newcontent="newcontent.txt"

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://lms.ealps.shinshu-u.ac.jp/2021/t/")

username=driver.find_element_by_id("username")
password=driver.find_element_by_id("password")
username.send_keys(login_username)
password.send_keys(login_password)
login= driver.find_element_by_name("_eventId_proceed")
login.click()
driver.implicitly_wait(1)

courses=driver.find_elements_by_class_name('coursename')
driver.implicitly_wait(1)

course=[]

for i in courses:
    course.append(i.text)
    
for i in course:
    link_ele=driver.find_element_by_link_text(i)
    driver.implicitly_wait(1)
    link_ele.click()
    driver.implicitly_wait(1)
    page=driver.find_element_by_id("region-main")
    with open(pass_newcontent, mode='a') as f:
        f.write("%"+i+"<"+str(driver.current_url)+">"+"\n")
        try:
            f.write(str(page.text)+"\n")
        except:
            f.write("\n")
    driver.implicitly_wait(1)
    driver.back()
    driver.implicitly_wait(1)

driver.close()


oldcontent=[]
newcontent=[]


with open(pass_newcontent) as f:
    for line in f:
        if line[0]=="%":
            newcontent.append([line])
        else:
            newcontent[-1].append(line)

try:
    with open(pass_oldcontent) as f:
        for line in f:
            if line[0]=="%":
                oldcontent.append([line])
            else:
                oldcontent[-1].append(line)
except:
    shutil.copy(pass_newcontent, 'oldcontent.txt')
    oldcontent=newcontent

for i in range(len(oldcontent)):
    n,m,diffclass=mayer_ses(oldcontent[i],newcontent[i])
    
    if diffclass :
        print(newcontent[i][0][1:])
        newname=newcontent[i][0][1:]
        delete=""
        add=""
        for i in n:
            if i[0]=="-":
                delete+=i[1:]+"\n"
        for i in m:
            if i[0]=="+":
                add+=i[1:]+"\n"
                
        deleteval={}
        addval={}
        if delete!="":
            deletaval={
                "color":"#D00000",
                "fields":[
                    {
                        "value":delete,
                    }
                ]
            }
        if add!="":
            addval={
                "color":"#00FF00",
                "fields":[
                    {
                        "value":add,
                    }
                ]
            }
        requests.post(slack_url, data=json.dumps({
            "attachments" : [
                {
                    "fallback":"ealpsが更新されました",
                    "pretext":newname
                },
                deleteval,
                addval,
            ]
        }))

os.remove(pass_oldcontent)
os.rename("newcontent.txt","oldcontent.txt")