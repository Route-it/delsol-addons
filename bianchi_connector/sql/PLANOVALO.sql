SELECT deqs.last_execution_time AS [Time], dest.text AS [Query], dest.*
FROM sys.dm_exec_query_stats AS deqs
CROSS APPLY sys.dm_exec_sql_text(deqs.sql_handle) AS dest
ORDER BY deqs.last_execution_time DESC


SELECT Comprobantes.Nombre,PlanAhorroSolicitudes.UnidadID,*
FROM (PlanAhorroSolicitudes LEFT JOIN Unidades ON PlanAhorroSolicitudes.UnidadID = Unidades.UnidadID) 
LEFT JOIN Modelos ON Unidades.Modelo = Modelos.Modelo 
inner join Comprobantes on PlanAhorroSolicitudes.ControlGR = Comprobantes.Referencia
inner join Colores on colores.ColorID = unidades.color
WHERE comprobantes.Origen LIKE 'VTGTS%' And 
Referencia like '%GR%' And 
(Comprobantes.Anulada = 0) And 
Comprobantes.Fecha > '20171012'
ORDER BY 1

select * from PlanAhorroSolicitudes
where chassis is not null
and ControlGR is not null

SELECT Comprobantes.Origen,Comprobantes.Documento,Comprobantes.Letra,Comprobantes.Sucursal,
Comprobantes.Numero,Comprobantes.Referencia,Comprobantes.Nombre,Comprobantes.Fecha,
Comprobantes.Asiento,Comprobantes.Total,Comprobantes.ObjetoAsociado 
FROM Comprobantes WHERE Comprobantes.Fecha BETWEEN '20171016' AND '20171019'  
AND Comprobantes.Origen LIKE 'VTGTS%' 
ORDER BY Comprobantes.Fecha,Comprobantes.Documento,Comprobantes.Letra,Comprobantes.Sucursal,
Comprobantes.Numero,Comprobantes.Nombre,Comprobantes.Referencia;