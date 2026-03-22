# Calculadora de Ampacidad de Líneas de Transmisión

Aplicación web para calcular la ampacidad (corriente máxima admisible) de líneas de transmisión eléctrica basada en el estándar IEEE 738.

## 🚀 Características

- **Cálculo preciso**: Implementación del estándar IEEE 738 para ampacidad
- **Interfaz intuitiva**: Aplicación web con Streamlit
- **Análisis de sensibilidad**: Gráficos interactivos para visualizar el impacto de diferentes variables
- **Soporte multiple materiales**: ACSR, AAC, AAAC, Cobre
- **Condiciones ambientales personalizables**: Temperatura, viento, radiación solar, altitud

## 📋 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🛠️ Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/MalverdeX/C-lculo-de-ampacidad.git
cd "Cálculo de ampacidad"
```

2. Crear un entorno virtual (recomendado):
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## 🎯 Uso

### Ejecutar la aplicación

```bash
streamlit run main.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Parámetros de entrada

#### Parámetros del Conductor:
- **Material del Conductor**: ACSR, AAC, AAAC, o Cobre
- **Diámetro del Conductor**: Diámetro exterior en mm
- **Resistencia**: Resistencia eléctrica a 20°C en Ω/km
- **Temperatura Máxima**: Temperatura máxima permitida del conductor (°C)
- **Emisividad**: Propiedad radiativa del conductor (0.2-1.0)
- **Coeficiente de Absorción Solar**: Capacidad de absorción de radiación solar (0.2-1.0)

#### Condiciones Ambientales:
- **Temperatura Ambiente**: Temperatura del aire circundante (°C)
- **Velocidad del Viento**: Velocidad del viento perpendicular al conductor (m/s)
- **Radiación Solar**: Intensidad de radiación solar (W/m²)
- **Altitud**: Altitud sobre el nivel del mar (m)

## 📊 Resultados

La aplicación proporciona:
- **Ampacidad Máxima**: Corriente máxima admisible en Amperios
- **Potencia Máxima**: Capacidad de transmisión en MW
- **Margen de Seguridad**: Porcentaje de capacidad disponible
- **Balance Térmico Detallado**: Descomposición de pérdidas y ganancias de calor
- **Gráficos de Sensibilidad**: Impacto de temperatura ambiente y velocidad del viento

## 🔬 Fundamentos Teóricos

### Concepto de Ampacidad

La **ampacidad** (del inglés *ampacity*) se define como la corriente máxima que un conductor puede transportar continuamente sin exceder su temperatura máxima de diseño. Este concepto es fundamental en el diseño y operación de sistemas de transmisión de energía eléctrica.

### Principios Físicos

El cálculo de ampacidad se basa en el **balance térmico estacionario** del conductor:

```
Calor generado = Calor disipado
I²R = q_conv + q_rad - q_solar
```

#### Componentes del Balance Térmico:

**1. Calor por Efecto Joule (I²R)**
- Corriente eléctrica que fluye por el conductor
- Resistencia eléctrica que depende del material y temperatura
- Ecuación: `P_joule = I² × R(T)`

**2. Disipación por Convección (q_conv)**
- Transferencia de calor entre el conductor y el aire circundante
- Depende de la velocidad del viento, temperatura y geometría
- Ecuación: `q_conv = h_conv × A_s × (T_c - T_a)`

**3. Disipación por Radiación (q_rad)**
- Emisión de radiación térmica según la ley de Stefan-Boltzmann
- Depende de la emisividad del material y temperaturas absolutas
- Ecuación: `q_rad = ε × σ × A_s × (T_c⁴ - T_a⁴)`

**4. Ganancia por Radiación Solar (q_solar)**
- Absorción de energía solar directa y difusa
- Depende del coeficiente de absorción y radiación incidente
- Ecuación: `q_solar = α × Q_solar × A_p`

### Ecuaciones Detalladas

#### Convección Forzada (IEEE 738)

Para velocidades de viento > 0.1 m/s:

```
Re = ρ_air × v_wind × D / μ_air
Nu = 0.65 + 0.35 × Re^0.52
h_conv = Nu × k_air / D
```

Donde:
- **Re**: Número de Reynolds
- **Nu**: Número de Nusselt
- **h_conv**: Coeficiente de convección [W/(m²·K)]
- **ρ_air**: Densidad del aire [kg/m³]
- **v_wind**: Velocidad del viento [m/s]
- **D**: Diámetro del conductor [m]
- **μ_air**: Viscosidad dinámica del aire [Pa·s]
- **k_air**: Conductividad térmica del aire [W/(m·K)]

#### Convección Natural

Para velocidades de viento ≤ 0.1 m/s:

```
Gr = g × β × ΔT × D³ / ν²
Nu = 0.48 × Gr^0.25
```

Donde:
- **Gr**: Número de Grashof
- **g**: Aceleración gravitacional [9.81 m/s²]
- **β**: Coeficiente de expansión térmica [1/K]
- **ΔT**: Diferencia de temperatura [K]
- **ν**: Viscosidad cinemática del aire [m²/s]

#### Radiación Térmica

```
q_rad = ε × σ × π × D × (T_c⁴ - T_a⁴)
```

Donde:
- **ε**: Emisividad superficial [0.2-1.0]
- **σ**: Constante de Stefan-Boltzmann [5.67×10⁻⁸ W/(m²·K⁴)]
- **T_c**: Temperatura del conductor [K]
- **T_a**: Temperatura ambiente [K]

#### Resistencia a Temperatura Variable

```
R(T) = R_20°C × [1 + α × (T - 20°C)]
```

Donde:
- **α**: Coeficiente de temperatura de resistencia
- **R_20°C**: Resistencia a 20°C [Ω/km]

### Materiales de Conductores

#### ACSR (Aluminum Conductor Steel Reinforced)
- Núcleo de acero con hilos de aluminio externos
- Alta resistencia mecánica, buena conductividad
- α ≈ 0.00393 1/°C

#### AAC (All Aluminum Conductor)
- 100% aluminio, sin refuerzo de acero
- Mayor conductividad, menor peso
- Uso en líneas de distribución

#### AAAC (All Aluminum Alloy Conductor)
- Aleación de aluminio con alta resistencia
- Mejor resistencia a la corrosión
- Mayor capacidad mecánica que AAC

#### Cobre (CU)
- Mayor conductividad eléctrica
- Mayor peso y costo
- Uso en aplicaciones especiales

### Factores Ambientales

#### Temperatura Ambiente
- Afecta directamente la capacidad de disipación
- Mayor temperatura = menor ampacidad
- Valores típicos: 10-40°C

#### Velocidad del Viento
- Principal mecanismo de enfriamiento
- Mayor velocidad = mayor convección = mayor ampacidad
- Dirección perpendicular al conductor es óptima

#### Radiación Solar
- Agrega calor al conductor
- Reduce la ampacidad disponible
- Máximo al mediodía solar

#### Altitud
- Reduce la densidad del aire
- Disminuye la convección
- Efecto significativo > 1000 m

### Límites de Temperatura

#### Temperatura Máxima del Conductor
- **ACSR**: 75-90°C (dependiendo del tipo)
- **AAC**: 75-85°C
- **AAAC**: 75-90°C
- **Cobre**: 70-90°C

#### Consideraciones de Diseño
- **Clearance térmico**: Expansión por calor
- **Degradación del material**: Envejecimiento acelerado
- **Sag del conductor**: Flecha por expansión térmica

### Ampacidad Dinámica vs Estática

#### Ampacidad Estática
- Basada en condiciones ambientales conservadoras
- Valores constantes para diseño
- Mayor factor de seguridad

#### Ampacidad Dinámica (DLR - Dynamic Line Rating)
- Monitoreo en tiempo real de condiciones
- Aprovecha condiciones favorables
- Mayor eficiencia del sistema

### Estándares y Referencias

- **IEEE Std 738-2012**: Standard for Calculating the Current-Temperature Relationship of Bare Conductors
- **IEEE Std 738-2006**: Versión anterior
- **IEC 60826**: Loading and strength of overhead transmission lines
- **CIGRE Technical Brochure 299**: Thermal rating of overhead conductors

## 📝 Notas Técnicas

- Los cálculos siguen el estándar IEEE 738-2012
- Se considera convección forzada cuando la velocidad del viento > 0.1 m/s
- La densidad del aire se corrige por altitud y temperatura
- Los resultados son aproximados y deben ser validados para aplicaciones críticas

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:

1. Fork del repositorio
2. Crear una rama (`git checkout -b feature/nueva-caracteristica`)
3. Commit de los cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## ⚠️ Descargo de Responsabilidad

Esta herramienta es para fines educativos y de referencia. Para aplicaciones críticas de ingeniería, consulte siempre los estándares oficiales y realice análisis detallados por ingenieros calificados.

## � Bibliografía y Referencias Teóricas

### Documentos de Referencia

La aplicación está respaldada por una completa bibliografía técnica disponible en la carpeta `/teoria/`:

#### 📄 Fundamentales
- **`Capacidad.pdf`**: Conceptos básicos de capacidad térmica
- **`PresentaciónTeria.pdf`**: Teoría completa de transferencia de calor
- **`2005_s1 compendio (verdejo).ppt.pdf`**: Compendio académico de referencia

#### ⚡ Aplicación Práctica
- **`CapacidadLinea.pdf`**: Cálculo detallado para líneas de transmisión
- **`Presentacion.PPTX`**: Ejemplos numéricos y casos de estudio
- **`Presentación.PPTX`**: Aplicaciones prácticas en sistemas reales

#### 🌊 Ampacidad Dinámica
- **`Dynamic_Ampacity_Unlocked.pdf`**: Tecnología DLR y monitoreo en tiempo real
- **`El_Límite_Dinámico.pdf`**: Optimización y límites del sistema

### 📖 Resumen Teórico Completo

Se ha creado un resumen teórico exhaustivo en `teoria/resumen_teorico.md` que incluye:

- **Balance térmico detallado** con todas las ecuaciones
- **Propiedades de materiales** (ACSR, AAC, AAAC, Cobre)
- **Factores ambientales** y su impacto cuantitativo
- **Métodos de cálculo** (estático vs dinámico)
- **Estándares internacionales** (IEEE 738, IEC 60826, CIGRE)

### 📋 Índice Bibliográfico

El archivo `teoria/indice_bibliografia.md` organiza toda la documentación por:
- Temas y aplicaciones específicas
- Nivel de complejidad
- Autores y referencias clave
- Casos de estudio documentados

### 🔗 Relación con el Currículo Académico

Este proyecto integra conceptos de:

#### **Transferencia de Calor**
- Convección forzada y natural
- Radiación térmica (Ley de Stefan-Boltzmann)
- Balance energético en estado estacionario

#### **Sistemas Eléctricos de Potencia**
- Diseño de líneas de transmisión
- Análisis térmico de conductores
- Operación y control de redes

#### **Ingeniería Ambiental**
- Efectos meteorológicos en sistemas eléctricos
- Correlaciones de transferencia de calor
- Factores de corrección atmosféricos

#### **Materiales Eléctricos**
- Propiedades térmicas y eléctricas
- Comportamiento a temperatura variable
- Degradación y envejecimiento

---

## �📞 Contacto

Para preguntas o sugerencias, por favor abre un issue en el repositorio de GitHub.
