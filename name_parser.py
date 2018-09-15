import re

def parse_wos_authors2(author):
    #print(author)
    if author is None:
        return  None 
    author_dict=dict()
    author_names =re.findall(r"[\w']+", author)
    author_dict['lname'] =  author_names[0]
    f_mname = author[len( author_dict['lname'])+1:].strip()
    # Allen's code from now on
    if len(f_mname) == 1:
        fname = f_mname
        mname = None
    elif len(f_mname) == 2:
        fname = f_mname[0]
        mname = f_mname[1]
    elif "." not in f_mname and len(f_mname) == 3:
        fname = f_mname[0:1]
        mname = f_mname[1:3]
    elif "." in f_mname:
        fname = []
        f_strip = str(f_mname).replace('.',' ').split()
        mname = f_strip[-1]
        for x in f_strip[:-1]:
                fname.append(x)
        fname = ''.join(fname)
    else:
        fname = f_mname
        mname = None
    author_dict['fname'] = fname
    author_dict['mname'] = mname
    #print(author_dict)
    return [author_dict]

def parse_wos_authors(author):
    author_dict=dict()
    if author is None:
        return  None
    if len(author[0])>0 and author[0]=='*':
        author = author[1:]
    author_names =re.findall(r"[\w']+", author)
    author_dict['fname'] = ''
    author_dict['mname'] = ''
    author_dict['lname'] = ''
    if len(author_names) >= 3:
            author_dict['lname'] = author_names[0]
            author_dict['fname'] = author_names[1]
            author_dict['mname'] = ''.join(name  for name in author_names[2:])
    if len(author_names) == 2:
        author_dict['lname'] = author_names[0]
        if len(author_names[1]) == 2:
            author_dict['mname']= author_names[1][1]
            author_dict['fname'] = author_names[1][0]
        else:
            author_dict['fname']=author_names[1]
    if len(author_names)==1:
        author_dict['lname'] = author_names[0]
    #print(author_dict)
    return [author_dict]
def parse_csx_authors(authors):
    if authors is None:
        return  None 
    authors = authors.split(',') 
    authors_list =[]
    for author in authors:
        author_dict = dict()
        author_names =re.findall(r"[\w']+", author)
        author_dict['fname'] = ''
        author_dict['mname'] = ''
        author_dict['lname'] = ''
        if len(author_names)>=3:
            author_dict['fname'] = author_names[0]
            author_dict['mname'] = author_names[1]
            author_dict['lname'] = ''.join(name  for name in author_names[2:])
        if len(author_names)==2:
            author_dict['fname'] = author_names[0]
            author_dict['lname']=author_names[1]
        if len(author_names)==1:
            author_dict['lname'] = author_names[0]
        authors_list.append(author_dict)
    return authors_list


