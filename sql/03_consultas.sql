-- Consultas sobre la base de ventas (canales + pacientes + sesiones)
-- Cada consulta empieza con "-- nombre:" para que el notebook las lea por separado.

-- nombre: ingresos_por_canal
SELECT c.nombre AS canal, c.tipo,
       COUNT(DISTINCT p.id_paciente) AS pacientes,
       COUNT(s.id_sesion)            AS sesiones,
       SUM(s.monto)                  AS ingresos,
       ROUND(SUM(s.monto) / COUNT(DISTINCT p.id_paciente), 0) AS ingreso_por_paciente
FROM canales c
JOIN pacientes p ON p.id_canal = c.id_canal
JOIN sesiones  s ON s.id_paciente = p.id_paciente
GROUP BY c.id_canal
ORDER BY ingresos DESC;

-- nombre: ingresos_por_plan
SELECT p.plan,
       COUNT(DISTINCT p.id_paciente) AS pacientes,
       SUM(s.monto) AS ingresos,
       ROUND(100.0 * SUM(s.monto) / (SELECT SUM(monto) FROM sesiones), 1) AS pct_ingresos
FROM pacientes p
JOIN sesiones s ON s.id_paciente = p.id_paciente
GROUP BY p.plan
ORDER BY ingresos DESC;

-- nombre: ingresos_por_mes
SELECT substr(fecha, 1, 7) AS mes, COUNT(*) AS sesiones, SUM(monto) AS ingresos
FROM sesiones
GROUP BY mes
ORDER BY mes;
