# Resumen Teórico de Ampacidad de Líneas de Transmisión

## Introducción

Este documento resume los conceptos fundamentales de ampacidad de líneas de transmisión eléctrica, basado en la bibliografía técnica y estándares internacionales.

## Conceptos Fundamentales

### Ampacidad (Current-Carrying Capacity)

La ampacidad es la corriente máxima continua que un conductor puede transportar sin exceder su temperatura límite de diseño. Este límite térmico está determinado por:

1. **Propiedades del material**: Resistencia mecánica y envejecimiento
2. **Clearance eléctrico**: Expansión térmica y distancias de seguridad
3. **Pérdidas de energía**: Eficiencia del sistema

### Balance Térmico

El principio fundamental es el equilibrio entre calor generado y calor disipado:

```
I²R = q_convección + q_radiación - q_solar
```

## Transferencia de Calor

### 1. Convección

#### Convección Forzada (viento > 0.1 m/s)

```
Re = ρ_air × v_wind × D / μ_air
Nu = 0.65 + 0.35 × Re^0.52
h_conv = Nu × k_air / D
q_conv = h_conv × π × D × (T_c - T_a)
```

#### Convección Natural (viento ≤ 0.1 m/s)

```
Gr = g × β × ΔT × D³ / ν²
Nu = 0.48 × Gr^0.25
q_conv = Nu × k_air / D × π × D × (T_c - T_a)
```

### 2. Radiación Térmica

Basada en la ley de Stefan-Boltzmann:

```
q_rad = ε × σ × π × D × (T_c⁴ - T_a⁴)
```

### 3. Radiación Solar

```
q_solar = α × Q_solar × D
```

## Propiedades de los Materiales

### Conductores Comunes

| Material | Resistencia (Ω/km) | Temp. Máx (°C) | α (1/°C) | Aplicación |
|----------|-------------------|----------------|----------|------------|
| ACSR | 0.09-0.15 | 75-90 | 0.00393 | Transmisión |
| AAC | 0.08-0.12 | 75-85 | 0.00393 | Distribución |
| AAAC | 0.10-0.16 | 75-90 | 0.00393 | Costas |
| CU | 0.05-0.08 | 70-90 | 0.00393 | Especial |

### Propiedades Térmicas

| Propiedad | Rango Típico | Impacto |
|-----------|--------------|---------|
| Emisividad (ε) | 0.2-1.0 | Mayor ε = más radiación |
| Absorción Solar (α) | 0.2-1.0 | Mayor α = más calor solar |
| Conductividad Térmica | 200-400 W/(m·K) | Mejora disipación |

## Factores Ambientales

### Temperatura Ambiente

- **Efecto**: Reduce gradiente térmico para disipación
- **Impacto**: 10°C ↑ = ~15% ampacidad ↓
- **Valores**: -20°C a 50°C (típicamente 10-40°C)

### Velocidad del Viento

- **Efecto**: Principal mecanismo de enfriamiento
- **Impacto**: 1 m/s ↑ = ~20% ampacidad ↑
- **Dirección óptima**: Perpendicular al conductor

### Radiación Solar

- **Efecto**: Agrega calor al conductor
- **Impacto**: 1000 W/m² = ~10% ampacidad ↓
- **Máximo**: Mediodía solar, verano

### Altitud

- **Efecto**: Reduce densidad del aire
- **Impacto**: 1000 m ↑ = ~5% ampacidad ↓
- **Corrección**: ρ_air = ρ_sea_level × exp(-altitude/8000)

## Métodos de Cálculo

### Ampacidad Estática (SLR - Static Line Rating)

- **Condiciones**: Conservadoras (40°C, 0.6 m/s, 1000 W/m²)
- **Ventaja**: Simple, seguro
- **Desventaja**: Subutilización del sistema

### Ampacidad Dinámica (DLR - Dynamic Line Rating)

- **Condiciones**: Tiempo real
- **Ventaja**: Mayor utilización
- **Desventaja**: Requiere monitoreo

### Ampacidad Estacional

- **Condiciones**: Por estaciones del año
- **Ventaja**: Balance entre simplicidad y eficiencia

## Estándares Internacionales

### IEEE 738-2012

**Standard for Calculating the Current-Temperature Relationship of Bare Conductors**

- **Método**: Balance térmico completo
- **Precisión**: ±5%
- **Aplicación**: Nivel internacional

### IEC 60826

**Loading and strength of overhead transmission lines**

- **Enfoque**: Mecánico y térmico
- **Factores**: Viento, hielo, temperatura
- **Región**: Principalmente Europa

### CIGRE 299

**Thermal rating of overhead conductors**

- **Investigación**: Estado del arte
- **Métodos**: Avanzados y experimentales
- **Referencia**: Comunidad técnica

## Consideraciones de Diseño

### Temperaturas Límite

| Factor | Límite Típico | Razón |
|--------|---------------|-------|
| ACSR | 75-90°C | Recocido del aluminio |
| AAC | 75-85°C | Pérdida de resistencia |
| AAAC | 75-90°C | Propiedades mecánicas |
| Cobre | 70-90°C | Oxidación |

### Clearance Térmico

- **Expansión**: ΔL = α_L × L × ΔT
- **Flecha**: Sag ∝ T² / Tension
- **Seguridad**: Distancias mínimas eléctricas

### Degradación del Material

- **Envejecimiento**: Tasa ∝ exp(-Ea/RT)
- **Recocido**: Tiempo ∝ T^n
- **Vida útil**: 40-50 años (diseño)

## Aplicaciones Prácticas

### Planificación

- **Diseño inicial**: Ampacidad estática
- **Expansión**: Ampacidad dinámica
- **Emergencias**: Sobrecargas temporales

### Operación

- **Monitoreo**: Temperatura en tiempo real
- **Control**: Re-despacho de carga
- **Mantenimiento**: Inspecciones térmicas

### Optimización

- **Reconductoring**: Conductores de mayor capacidad
- **Compactación**: Reducción de clearance
- **Tecnología**: HTLS (High Temperature Low Sag)

## Validación Experimental

### Métodos de Medición

1. **Termopares**: Contacto directo
2. **Infrarrojo**: No contacto
3. **Resistencia**: Eléctrica
4. **Fibra óptica**: Distribuida

### Ensayos Típicos

- **Corriente escalonada**: Validación de modelos
- **Ciclos térmicos**: Envejecimiento acelerado
- **Campo**: Condiciones reales

## Tendencias Futuras

### Tecnologías Emergentes

- **HTLS**: Operación a 150-250°C
- **Monitoreo IoT**: Sensores distribuidos
- **IA/ML**: Predicción de ampacidad
- **Drones**: Inspección automatizada

### Integración con Redes Inteligentes

- **SCADA**: Integración en tiempo real
- **WAMS**: Sincrofasores
- **DER**: Recursos distribuidos
- **Microredes**: Operación local

## Referencias Bibliográficas

1. **IEEE Std 738-2012**: Current-Temperature Relationship
2. **CIGRE Brochure 299**: Thermal Rating
3. **IEC 60826**: Loading and Strength
4. **Black & Rehder (1985)**: Transmission Line Reference Book
5. **Douglass (1976)**: Weather-Dependent Ratings

---

*Este resumen está basado en los documentos técnicos disponibles en la carpeta de teoría y está alineado con los estándares internacionales para el cálculo de ampacidad en líneas de transmisión.*
