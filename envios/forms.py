from django import forms
from envios.models import Cliente, Oficina
import re

def validar_cedula_ecuador(cedula):
    """Valida una cédula ecuatoriana usando el algoritmo del último dígito verificador."""
    if not cedula.isdigit() or len(cedula) != 10:
        return False
    
    provincia = int(cedula[:2])
    if provincia < 1 or provincia > 24:
        return False

    tercer_digito = int(cedula[2])
    if tercer_digito >= 6:
        return False

    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0
    for i in range(9):
        val = int(cedula[i]) * coeficientes[i]
        suma += val - 9 if val >= 10 else val

    digito_verificador = (10 - (suma % 10)) % 10
    return digito_verificador == int(cedula[9])


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['cedula', 'nombres', 'apellidos', 'email', 'telefono', 'direccion']
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 1712345678'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 0991234567'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula', '').strip()
        if not validar_cedula_ecuador(cedula):
            raise forms.ValidationError("La cédula ingresada no es válida para Ecuador.")
        
        # Verificar unicidad al editar
        query = Cliente.objects.filter(cedula=cedula)
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise forms.ValidationError("Ya existe un cliente con esta cédula.")
        
        return cedula

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        if not re.match(r'^\d{7,10}$', telefono):
            raise forms.ValidationError("El teléfono debe contener entre 7 y 10 dígitos numéricos.")
        return telefono


class OficinaForm(forms.ModelForm):
    class Meta:
        model = Oficina
        fields = ['nombre', 'ciudad', 'direccion', 'telefono', 'email']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        if not re.match(r'^\d{7,10}$', telefono):
            raise forms.ValidationError("El teléfono debe contener entre 7 y 10 dígitos numéricos.")
        return telefono