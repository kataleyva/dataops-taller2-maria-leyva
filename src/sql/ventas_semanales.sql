-- Ventas semanales por tienda, usando el registro maestro de ubicaciones
SELECT
    v.semana,
    u.id_ubicacion_maestro AS id_tienda,
    AVG(v.precio) AS precio_promedio,
    MAX(v.promocion) AS promocion,
    SUM(v.cantidad) AS ventas
FROM ventas v
JOIN mdm_ubicacion u ON v.codigo_tienda = u.codigo_tienda
WHERE u.estado = 'ACTIVA'
GROUP BY v.semana, u.id_ubicacion_maestro;