from bs4 import BeautifulSoup
import os, pickle

class MyExceptin(Exception):
    def __init__(self,str):
        self.str = str
    def __str__(self):
        print("该情况暂未处理:"+self.str)

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
        package_class_dict = dict()
        with open(path, 'r', encoding='utf-8') as f:
            html_doc = f.read()
        bs = BeautifulSoup(html_doc, "html.parser")
        pack_name = bs.find('div', attrs={'class': 'header'})
        pack_name = pack_name.find('a', attrs={'href': 'package-summary.html'}).get_text()
        # undo 删除如List<E>中的<E>
        class_name = bs.find('h1', attrs={'class': 'title'}).get_text().split()[1].split('<')[0]

        # if class_name == 'List':
        #     print("List")
        meth_api_names = list()
        if api2desc.__contains__(pack_name):
            api2desc[pack_name][class_name] = meth_api_names
        else:
            class_apis = dict()
            class_apis[class_name] = meth_api_names
            api2desc[pack_name] = class_apis
        constructor_summary = bs.find("section", attrs={'class': 'constructor-summary'})
        if constructor_summary:
            for item in constructor_summary.find_all("div", attrs={'class': 'col-constructor-name even-row-color'}):
                # params = item.find("span", attrs={'class': 'member-name-link'}).get_text()
                # params = item.code.find('a')['href']
                meth_name_attrs = item.code.find('a')['href'].strip(')').split('(')
                if len(meth_name_attrs) > 2:
                    print(2)
                if len(meth_name_attrs) > 1:
                    meth_attrs = meth_name_attrs[1]
                    if '%5B%5D' in meth_attrs:
                        meth_attrs = meth_attrs.replace('%5B%5D', '[]')
                else:
                    meth_attrs = None
                meth_api_names.append([class_name, meth_attrs, None, 'public'])
            for item in constructor_summary.find_all("div", attrs={'class': 'col-constructor-name odd-row-color'}):
                # params = item.find("span", attrs={'class': 'member-name-link'}).get_text()
                # params = item.code.find('a')['href']
                meth_name_attrs = item.code.find('a')['href'].strip(')').split('(')
                if len(meth_name_attrs) > 2:
                    print(2)
                if len(meth_name_attrs) > 1:
                    meth_attrs = meth_name_attrs[1]
                    if '%5B%5D' in meth_attrs:
                        meth_attrs = meth_attrs.replace('%5B%5D', '[]')
                else:
                    meth_attrs = None
                meth_api_names.append([class_name, meth_attrs, None, 'public'])

        # print('--------------------------------------------')
        # undo 没有收录继承方法
        meth_detail = bs.find("section", attrs={'class': 'method-details'})
        if meth_detail:
            for item in meth_detail.find_all("section", attrs={'class': 'detail'}):
                meth_name_attrs = item['id'].strip(')').split('(')
                if len(meth_name_attrs) > 1:
                    meth_attrs = meth_name_attrs[1]
                else:
                    meth_attrs = None
                meth_name = item.h3.get_text()
                # undo 出去所有<>,如['lines', '', 'Stream<String>']
                return_type = item.find("span", attrs={'class': 'return-type'}).get_text().split('<')[0]
                try:
                    modifiers = item.find("span", attrs={'class': 'modifiers'}).get_text()
                except AttributeError:
                    modifiers = 'public'
                meth_api_name = [meth_name, meth_attrs, return_type, modifiers]
                meth_api_names.append(meth_api_name)
                # meth_desc = item.find("div", attrs={'class': 'block'}).get_text()
                # print(meth_api_name)
                # print(meth_desc)
                # api2desc[meth_api_name] = meth_desc
                # print('--------------------------------------------')
        meth_inherited = bs.find("section", attrs={'class': 'method-summary'}).findAll("div", attrs={'inherited-list'})
        iter_num = 0
        # if class_name == 'FileWriter':
        #     print("FileWrite")
        # items = meth_inherited.findAll('code')
        for item in meth_inherited:
            item = item.code
            # meth_name_attrs_list = item.a['href'].strip(')').split('(')
            meth_name_attrs_list = item.findAll('a')

            for meth_name_attrs in meth_name_attrs_list:
                meth_name_attrs = meth_name_attrs['href'].strip(')').split('(')
                if len(meth_name_attrs) > 1:
                    meth_attrs = meth_name_attrs[1]
                    if '%5B%5D' in meth_attrs:
                        meth_attrs = meth_attrs.replace('%5B%5D', '[]')
                else:
                    meth_attrs = None
                meth_name = meth_name_attrs[0].split('#')[1]
                return_type = 'Undefined'
                meth_api_name = [meth_name, meth_attrs, return_type, 'public']
                if (iter_num == 0) or (meth_api_name not in meth_api_names):
                    meth_api_names.append(meth_api_name)
            iter_num += 1
        # //新增，为了构建structure文件
        if package_class_dict.__contains__(pack_name):
            package_class_dict[pack_name] = dict()
        class_interface = bs.find("meta", attrs={'name': 'keywords'})['content'].split()[-1]
        package_class_dict[pack_name][class_name] = [meth_api_names, path.replace('\\', '/'), class_interface]
    except AttributeError:
        pass
    except TypeError:
        pass
    return api2desc, package_class_dict

def get_class_pack_dict(api2desc):
    class_pack_dict = dict()

    def get_pack_name(package_class_name):
        class_name = package_class_name.split('.')[-1]
        package_name = package_class_name.rstrip(class_name).rstrip('.')
        return class_name, package_name

    for pack_name in api2desc.keys():
        classes = api2desc.get(pack_name)
        for class_name in classes.keys():
            try:
                if class_pack_dict.__contains__(class_name):
                    # undo classneme作为key可能出现重复
                    raise MyExceptin(f'该{class_name}类已出现过')
                else:
                    class_pack_dict[class_name] = pack_name
            except MyExceptin as e:
                print(e.str)
                pass
    return class_pack_dict

    def get_structure(package_class_dict):
        project_structure_dict = dict()
        basic_type = ['byte[]', 'char', 'short', 'int', 'long', 'float', 'double', 'boolean', 'void', 'char[]']

        def get_method(package_name, class_name, package_project, package_path):
            for method in package_class_dict.get(package_name).get(class_name):
                # 构造器
                if method[0] == class_name:
                    method[0] = 'new'
                else:
                    params = []
                    for param in method[-3]:
                        if param in basic_type:
                            params.append(param)
                        else:
                            param_class_name, param_class_pack = get_pack_name(param)
                            param_path = param_class_pack.get(param_class_pack).rstrip(f'/{param_class_name}.html')
                            param_hash = f'{method}${package_project}${param_path}${param_class_pack}${param_class_name}'
                            params.append(param_hash)

                    params_hash = ','.join(params)
                    if method[-2] not in basic_type:
                        return_class_name, return_class_pack = get_pack_name(method[-2])
                        return_path = package_class_dict.get(return_class_pack).rstrip(f'/{return_class_name}.html')
                        return_hash = f'{method}${package_project}${return_path}${return_class_pack}${return_class_name}'
                    method_hash = f'method${package_project}${package_path}${package_name}${class_name}$' \
                                  f'{method[-1]},{method[0]}({params_hash})->{return_hash}'
                    project_structure_dict[method_hash] = {
                        'type': 'method',
                        'project': package_project,
                        'path': package_path,
                        'package': package_name,
                        'class': class_name,
                        'method': method[0],
                        'field': method[-1],
                        'hash': method_hash
                    }


        def package_class_structures():
            for package_name in package_class_dict.keys():
                package_project = 'jdk-16.0.2_doc-all'
                package_hash = f'package${package_project}${package_name}'
                package_path = ''
                project_structure_dict[package_hash] = {
                    'type': 'package',
                    'project': package_project,
                    'path': package_path,
                    'package': package_name,
                    'contain classes': [],
                    'hash': package_hash
                }
                for class_name, decs in package_class_dict.get(package_name).items():
                    if decs[-1] == 'class':
                        class_hash = f'class${package_project}${package_path}${package_name}${class_name}'
                        project_structure_dict[class_hash] = {
                            'type': 'class',
                            'project': package_project,
                            'path': package_path,
                            'package': package_name,
                            'class': class_name,
                            'extend': '',
                            'implement': '',
                            'hash': class_hash
                        }
                    else:
                        class_hash = f'interface${package_project}${package_path}${package_name}${class_name}'
                        project_structure_dict[class_hash] = {
                            'type': 'interface',
                            'project': package_project,
                            'path': package_path,
                            'package': package_name,
                            'interface': class_name,
                            'extend': '',
                            'hash': class_hash
                        }
                    project_structure_dict.get(package_hash).get('contain classes').append(class_hash)
                    get_method(package_name, class_name, package_project, package_path)

        package_class_structures()

if __name__ == '__main__':
    api2desc = {}
    package_class_dict = {}
    root_path = r'.\jdk-16.0.2_doc-all\api'
    files = [file for file in get_files(root_path) if legal_file(file)]
    for i, file in enumerate(files):
        print('{}/{}: len(api2desc)={}'.format(i+1, len(files), len(api2desc)), end='\r')
        if i>30:
            api2desc, package_class_dict = file_parser(file, api2desc)
    class_pack_dict = get_class_pack_dict(api2desc)
    java_type = ['byte[]', 'char', 'short', 'int', 'long', 'float', 'double', 'boolean', 'void']
    for i in api2desc.values():
        for j in i.values():
            for k in j:
                try:
                    # undo：需要得到返回值类所在的包
                    if k[2] not in java_type:
                        k[2] = f'{class_pack_dict.get(k[2])}.{k[2]}'
                except MyExceptin as e:
                    print(f'{k[2]}没在class_pack_dict中')
    print(api2desc)
    # print(c, len(api2desc))
    # save_pkl('../../AST_parse/api2desc.pkl', api2desc)
    save_pkl('./api2desc.pkl', api2desc)
    print('nice')
#     eclipse支持的java开发插件需要吗

