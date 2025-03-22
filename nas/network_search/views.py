from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import NetworksDB, PhysicalDB
from .forms import IPHostToSubnetForm, UpdateNetworksDBForm, UpdatePhysicalDBForm

import csv
    
    
class IPHostToSubnetView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'network_search.view_networksdb'
    raise_exception = True
    _TEMPLATE = 'iptosubnet.html'
    
    def get(self, request: HttpRequest):
        form = IPHostToSubnetForm()
        return render(request, self._TEMPLATE, {'form': form})

    def post(self, request: HttpRequest):
        HEADER = ['INPUT', 'sysName', 'interfaceName', 'interfaceIP']
        
        # Первоначальная проверка на наличие данных в таблицах
        if not NetworksDB.objects.all() or not PhysicalDB.objects.all():
            return render(request, self._TEMPLATE, {'subnet_list': 'ERROR: таблицы пусты', 'output_height': '94%'})


        if request.method == 'POST' and 'find' in request.POST:
            # Поиск информации в таблице NetworksDB и составление изначального стандартного ответа
            def process_hosts(host_addresses: list[str]) -> list[list[str]]:
                def is_ip_in_network(host_ip: str, network_ip_with_prefix: str) -> bool:
                    network_ip, prefix = network_ip_with_prefix.split('/')
                    host_ip = host_ip.strip()
                    
                    # Проверка введенных данных на соответствие IP
                    import re
                    ip_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
                    if not re.search(ip_pattern, host_ip):
                        return False
                        
                    # Преобразование IP-адреса и маски в 32-битные целые числа
                    def ip_to_int(ip):
                        parts = list(map(int, ip.split('.')))
                        return (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]

                    host_int = ip_to_int(host_ip)
                    network_int = ip_to_int(network_ip)
                    
                    # Преобразование длины маски в 32-битную маску
                    def prefix_to_subnet(prefix):
                        prefix = int(prefix)
                        mask = (0xFFFFFFFF >> (32 - prefix)) << (32 - prefix)
                        return mask
                    
                    mask_int = prefix_to_subnet(prefix)

                    # Проверка, находится ли хост в сети
                    return (host_int & mask_int) == (network_int & mask_int)
                
                output = []
                for host_address in host_addresses.split('\n'):
                    try:
                        region = '.'.join(host_address.split('.')[:2])
                        similar_nets = NetworksDB.objects.filter(int_ipaddr__contains=region)
                        flag = len(output)
                        for net in similar_nets:
                            if is_ip_in_network(host_address, net.int_ipaddr):
                                info = [host_address.strip(), net.sys_name, net.int_name, net.int_ipaddr]
                                output.append(info)
                                break
                        if flag == len(output):
                            info = [host_address, f"Подсеть не найдена для: {host_address}"] + [''] * 2
                            output.append(info)
                    except ValueError:
                        info = [host_address, f"Некорректный адрес: {host_address}"] + [''] * 2
                        output.append(info)
                return output
            
            # Поиск в логической выгрузке
            def find_logical():
                request.session['download_what'] = 'csv'    # Сохранение текста для кнопки Скачать
                host_addresses = request.POST.get('host_addresses', '').strip()     # введенные данные
                if host_addresses:
                    return [request.session['delimeter_text'].join(line) for line in process_hosts(host_addresses)]
            
            # Поиск в физической выгрузке
            # сначала генерируется та же информация, что из лог. выгрузки, потом по столбцу sys_name берется код объекта, а он соответсвует коду объекта в физ. выгрузке
            def find_physical():
                request.session['download_what'] = 'txt'    # Сохранение текста для кнопки Скачать
                host_addresses = request.POST.get('host_addresses', '').strip()     # введенные данные
                if host_addresses:
                    subnet_list = process_hosts(host_addresses)
                    result = []
                    for sub in subnet_list:
                        if 'Подсеть не найдена для:' in sub[1] or 'Некорректный адрес:' in sub[1]:
                            result.append(''.join(sub[1:]))
                        else:
                            ipaddr = sub[0]
                            code = sub[1][:5]
                            try:
                                obj = PhysicalDB.objects.get(obj_code__contains=code)
                            except Exception:
                                result.append(f'Не найден объект, которому принадлежит IP-адрес {ipaddr}')
                            else:
                                result.append(f'IP-адрес {ipaddr} принадлежит объекту {obj.obj_name}, расположенному по адресу {obj.obj_addr}')
                    return result
                        
            # Сохранение разделителей в сессию
            request.session['delimeter_text'] = request.POST.get('delimeter_text', '')
            request.session['delimeter_csv'] = request.POST.get('delimeter_csv', '')
            
            # Генерация данных для вывода
            if request.user.groups.filter(name__contains='engineer'):
                res = [(request.session['delimeter_text']).join(HEADER)] + find_logical()
            elif request.user.groups.filter(name__contains='visitor'):
                res = find_physical()
            else:
                res = ['Ошибка...', 'Возможно, сервис не смог определить, какой ответ Вам выдать']
            
            return render(request, self._TEMPLATE, {'subnet_list': '\n'.join(res), 'output_height': '94%'})


        if request.method == 'POST' and 'download_csv' in request.POST:
            # Создание файла csv с логической выгрузкой (для engineer)
            def download_logical_csv():                
                response_ = HttpResponse(content_type='text/csv')
                response_['Content-Disposition'] = 'attachment; filename="subnet_list.csv"'

                writer = csv.writer(response_, delimiter=delimeter_csv)
                
                for item in subnet_list.split('\n'):
                    item = item.split(delimeter_text)
                    item[-1] = item[-1].replace('\r', '')
                    if len(item) != 4:
                        item[0] = item[0].replace('\r', '')
                        item = item + ([''] * 3)
                    writer.writerow(item)

                return response_
            
            # Создание файла txt с физической выгрузкой (для visitor)
            def download_physical_txt():
                response_ = HttpResponse(content_type='text/plain')
                response_['Content-Disposition'] = 'attachment; filename="subnet_list.txt"'

                for item in subnet_list.split('\n'):
                    response_.write(item + '\n')
                    
                return response_
            
            # Переменные
            subnet_list = request.POST.get('temp_subnet_list', '').strip()
            delimeter_text = request.session['delimeter_text']
            delimeter_csv = request.session['delimeter_csv']
            
            if request.user.groups.filter(name__contains='engineer'):
                response = download_logical_csv()
            elif request.user.groups.filter(name__contains='visitor'):
                response = download_physical_txt()
                
            return response
        
        # Стандратное отображение
        return render(request, self._TEMPLATE)
    

class UpdateNetworksDBView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'network_search.change_networksdb'
    raise_exception = True
    _TEMPLATE = 'updatedb.html'
    
    def get(self, request: HttpRequest):
        form = UpdateNetworksDBForm()
        request.session['update_what'] = 'логическая'
        return render(request, self._TEMPLATE, {'form': form})

    def post(self, request: HttpRequest):
        import io
        import csv
        
        HEADER = ['sysName', 'interfaceName', 'interfaceIP']
        
        form = UpdateNetworksDBForm(request.POST, request.FILES)
        if form.is_valid():
            # Проверка типа файла
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                return render(request, self._TEMPLATE, {'form': form, 'error': 'Необходимо загрузить файл в формате CSV'})
            
            # Чтение содержимого CSV файла
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string, delimiter=request.POST.get('delimeter_csv'))

            # Первичная проверка по заголовку
            for row in reader:
                if row != HEADER:
                    return render(request, self._TEMPLATE, {'form': form, 'error': 'Некорректное содержимое файла или неверно указан разделитель', 'details': 'Заголовок не равен референсному'})
                break
                        
            # Сохранение id последнего элемента
            try:
                last_id = NetworksDB.objects.latest('id').id
            except ObjectDoesNotExist:
                last_id = None

            # Заполнение модели NetworksDB
            for row in reader:
                # Пропуск первой строки
                if 'sysName' in row:
                    continue
                
                if len(row) == 3:
                    NetworksDB.objects.create(
                        sys_name = row[0],
                        int_name = row[1],
                        int_ipaddr = row[2]
                        )
            
            # Очистка старых значений
            if last_id:
                NetworksDB.objects.filter(id__lte=last_id).delete()
            
            # Подсчет сколько загружено
            count = NetworksDB.objects.all().count()
            
            return render(request, self._TEMPLATE, {'form': form, 'success': 'Данные успешно загружены', 'count': f'Строк загружено: {count}'})
        
        return render(request, self._TEMPLATE, {'form': form})


class UpdatePhysicalDBView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'network_search.change_physicaldb'
    raise_exception = True
    _TEMPLATE = 'updatedb.html'
    
    def get(self, request: HttpRequest):
        form = UpdatePhysicalDBForm()
        request.session['update_what'] = 'физическая'
        return render(request, self._TEMPLATE, {'form': form})

    def post(self, request: HttpRequest):
        import io
        import csv
        
        HEADER = ['Код объекта', 'Наименование объекта', 'Адрес']
        
        form = UpdatePhysicalDBForm(request.POST, request.FILES)
        if form.is_valid():
            # Проверка типа файла
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                return render(request, self._TEMPLATE, {'form': form, 'error': 'Необходимо загрузить файл в формате CSV'})
                    
            # Чтение содержимого CSV файла
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            del_csv = request.POST.get('delimeter_csv')
            reader = csv.reader(io_string, delimiter=del_csv)

            # Первичная проверка по заголовку
            for row in reader:
                if row != HEADER:
                    print(row)
                    return render(request, self._TEMPLATE, {'form': form, 'error': 'Некорректное содержимое файла или неверно указан разделитель', 'details': f'Заголовок не равен референсному("{del_csv.join(HEADER)}")'})
                break
            
            # Сохранение id последнего элемента
            try:
                last_id = PhysicalDB.objects.latest('id').id
            except ObjectDoesNotExist:
                last_id = None
            
            # Заполнение модели PhysicalDB
            for row in reader:
                if '№' in row:
                    continue
                
                # Код объекта состоит из 5 цифр
                if len(row[0]) == 5:
                    PhysicalDB.objects.create(
                        obj_code = row[0],
                        obj_name = row[1],
                        obj_addr = row[2])
            
            # Очистка старых значений
            if last_id:
                PhysicalDB.objects.filter(id__lte=last_id).delete()
            
            # Подсчет сколько загружено
            count = PhysicalDB.objects.all().count()
            
            return render(request, self._TEMPLATE, {'form': form, 'success': 'Данные успешно загружены', 'count': f'Строк загружено: {count}'})
        
        return render(request, self._TEMPLATE, {'form': form})
