from bs4 import BeautifulSoup
import os, pickle

def save_pkl(path, data):
    with open(path, 'wb') as f:
        pickle.dump(data, f)

def load_pkl(path):
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data

def get_files(root_path):
    files = []
    for filepath, dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            files.append(os.path.join(filepath, filename))
    return files

def extract_short(desc):
    p = desc.find('.')
    if p != -1:
        desc = desc[:p+1]
    return desc

def legal_file(file_name):
    if file_name.endswith('.html'):
        if not file_name.endswith('summary.html'):
            if not file_name.endswith('-index.html'):
                if file_name.find('class-use') == -1:
                    return True
    return False

def file_parser(path, api2desc):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            html_doc = f.read()
        bs = BeautifulSoup(html_doc, "html.parser")
        pack_name = bs.find('div', attrs={'class': 'header'})
        pack_name = pack_name.find('a', attrs={'href': 'package-summary.html'}).get_text()
        class_name = bs.find('h1', attrs={'class': 'title'}).get_text().split()[1]
        # pack_name = bs.find('div', attrs={'class': 'header'})
        # pack_name = pack_name.find('a', attrs={'href': f'{class_name}.html'}).get_text()
        # paths = path.split('\\')
        # paths_len = len(paths)
        # paths[paths_len - 1] = paths[paths_len - 1].strip('.html')
        # pack_name = paths[3]
        # for i in range(4, len(paths)):
        #     pack_name = f'{pack_name}.{paths[i]}'

        init_api_name = f'{pack_name}.{class_name}'
        # class_desc = bs.find('section', attrs={'class': 'description'}).find("div", attrs={'class': 'block'}).get_text()
        # init_api_name = pack_name
        # print('--------------------------------------------')
        # print(init_api_name)
        # print(class_desc)
        meth_api_names = list()
        api2desc[init_api_name] = meth_api_names
        # print('--------------------------------------------')
        meth_detail = bs.find("section", attrs={'class': 'method-details'})
        for item in meth_detail.find_all("section", attrs={'class': 'detail'}):
            meth_name_attrs = item['id'].strip(')').split('(')
            if len(meth_name_attrs) > 1:
                meth_attrs = meth_name_attrs[1]
            else:
                meth_attrs = None
            meth_name = item.h3.get_text()
            # 代办：需要得到返回值类所在的包
            return_type = item.find("span", attrs={'class': 'return-type'}).get_text()
            meth_api_name = [meth_name, meth_attrs, return_type]
            meth_api_names.append(meth_api_name)
            # meth_desc = item.find("div", attrs={'class': 'block'}).get_text()
            # print(meth_api_name)
            # print(meth_desc)
            # api2desc[meth_api_name] = meth_desc
            # print('--------------------------------------------')
    except AttributeError as e:
        pass
    return api2desc



if __name__ == '__main__':
    api2desc = {}
    root_path = r'.\jdk-16.0.2_doc-all\api'
    files = [file for file in get_files(root_path) if legal_file(file)]
    for i, file in enumerate(files):
        print('{}/{}: len(api2desc)={}'.format(i+1, len(files), len(api2desc)), end='\r')
        if i>30:
            api2desc = file_parser(file, api2desc)
    c = 0
    # for k, v in api2desc.items():
    #     if len(v) == 0:
    #         c += 1
    print(api2desc)
    # print(c, len(api2desc))
    # save_pkl('../../AST_parse/api2desc.pkl', api2desc)
    save_pkl('./api2desc.pkl', api2desc)
    print('nice')

