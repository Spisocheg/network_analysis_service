from django import forms


class IPHostToSubnetForm(forms.Form):
    host_addresses = forms.CharField(widget=forms.Textarea(attrs={ 'class': 'form-control', 'id': 'input_textarea', 'rows': '20' }), 
                                     label='IP-адреса (по одному на строку)',
                                     required=True)
    delimeter_text = forms.CharField(widget=forms.TextInput(attrs={ 'class': 'w-100', 'id': 'input_del_text', 'value': ' | ' }), 
                                     label='Разделитель (текст)',
                                     required=True)
    delimeter_csv = forms.CharField(widget=forms.TextInput(attrs={ 'class': 'w-100', 'id': 'input_del_csv', 'value': ';' }),
                                    label='Разделитель (csv)',
                                    required=True)


class UpdateNetworksDBForm(forms.Form):
    delimeter_csv = forms.CharField(widget=forms.TextInput(attrs={ 'class': 'mx-2', 'style': 'width: 10%; height: 5%;', 'id': 'input_del_csv' }),
                                    label='Разделитель (csv):',
                                    required=True)
    csv_file = forms.FileField(widget=forms.FileInput(attrs={ 'class': 'input-file', 'id': 'csv_file_input', 'accept': '.csv', 'onchange': 'displayLoad(this);' }), 
                               label='Выберите CSV файл', 
                               required=True)
    
    
class UpdatePhysicalDBForm(forms.Form):
    delimeter_csv = forms.CharField(widget=forms.TextInput(attrs={ 'class': 'mx-2', 'style': 'width: 10%; height: 5%;', 'id': 'input_del_csv' }),
                                    label='Разделитель (csv):',
                                    required=True)
    csv_file = forms.FileField(widget=forms.FileInput(attrs={ 'class': 'input-file', 'id': 'csv_file_input', 'accept': '.csv', 'onchange': 'displayLoad(this);' }), 
                               label='Выберите CSV файл', 
                               required=True)
    
