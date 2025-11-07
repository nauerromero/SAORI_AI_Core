"""
GPU Setup Verification - TRS Engine Core
Verifica que el entorno esté listo para entrenar el modelo de sentimiento
"""

import sys

print("=" * 60)
print("🔍 VERIFICACIÓN DE ENTORNO - GPU SETUP")
print("=" * 60)

# 1. Python version
print("\n[1/5] Python Version:")
print(f"   ✓ Python {sys.version.split()[0]}")
if sys.version_info < (3, 9):
    print("   ⚠️  Advertencia: Se recomienda Python 3.9+")

# 2. PyTorch y CUDA
print("\n[2/5] PyTorch y CUDA:")
try:
    import torch
    print(f"   ✓ PyTorch: {torch.__version__}")
    
    if torch.cuda.is_available():
        print(f"   ✓ CUDA disponible: Sí")
        print(f"   ✓ GPU: {torch.cuda.get_device_name(0)}")
        print(f"   ✓ CUDA Version: {torch.version.cuda}")
        
        # VRAM
        total_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"   ✓ VRAM Total: {total_memory:.2f} GB")
        
        # Test simple
        try:
            x = torch.rand(1000, 1000).cuda()
            y = torch.rand(1000, 1000).cuda()
            z = x @ y
            print(f"   ✓ Test de GPU: Exitoso")
            del x, y, z
            torch.cuda.empty_cache()
        except Exception as e:
            print(f"   ❌ Test de GPU falló: {e}")
    else:
        print(f"   ❌ CUDA NO disponible")
        print(f"   ℹ️  El entrenamiento será muy lento en CPU")
        print(f"   ℹ️  Instala: pip install torch --index-url https://download.pytorch.org/whl/cu121")
except ImportError:
    print("   ❌ PyTorch no instalado")
    print("   ℹ️  Instala: pip install torch --index-url https://download.pytorch.org/whl/cu121")

# 3. Transformers
print("\n[3/5] Transformers:")
try:
    import transformers
    print(f"   ✓ Transformers: {transformers.__version__}")
except ImportError:
    print("   ❌ Transformers no instalado")
    print("   ℹ️  Instala: pip install transformers")

# 4. Otras dependencias
print("\n[4/5] Dependencias adicionales:")
dependencies = {
    'datasets': 'datasets',
    'evaluate': 'evaluate',
    'sklearn': 'scikit-learn',
    'pandas': 'pandas',
    'numpy': 'numpy'
}

for module, package in dependencies.items():
    try:
        __import__(module)
        print(f"   ✓ {package}")
    except ImportError:
        print(f"   ❌ {package} no instalado")

# 5. Estructura de carpetas
print("\n[5/5] Estructura del proyecto:")
import os

folders_to_check = [
    'Models',
    'Data/sentiment_training',
    'Modules',
    'Logs/reports'
]

for folder in folders_to_check:
    if os.path.exists(folder):
        print(f"   ✓ {folder}")
    else:
        print(f"   ❌ {folder} no existe")
        print(f"      Crear con: mkdir {folder}")

# Resumen final
print("\n" + "=" * 60)
print("📊 RESUMEN")
print("=" * 60)

if 'torch' in sys.modules and torch.cuda.is_available():
    print("✅ GPU LISTA PARA ENTRENAR")
    print(f"\n⚡ Tu Alienware M18 R2 está configurada correctamente")
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
    print(f"   VRAM: {total_memory:.2f} GB")
    print(f"\n🚀 Tiempo estimado de entrenamiento: 1-1.5h (3 epochs)")
    print(f"   Batch size recomendado: 32-48")
else:
    print("⚠️  CONFIGURACIÓN INCOMPLETA")
    print("\n📝 Pasos para completar setup:")
    print("1. Instalar PyTorch con CUDA:")
    print("   pip install torch --index-url https://download.pytorch.org/whl/cu121")
    print("\n2. Instalar dependencias:")
    print("   pip install -r requirements_sentiment.txt")
    print("\n3. Verificar drivers NVIDIA actualizados")

print("\n" + "=" * 60)
print("Ejecuta este script nuevamente después de instalar dependencias")
print("=" * 60)

