<Instalar app>

SELECT *
  FROM delsol_delivery;

select * from hr_department

ALTER TABLE delsol_rqr
   ADD COLUMN sector_hr integer;

UPDATE delsol_rqr
   SET sector_hr=sector;

ALTER TABLE delsol_rqr
   drop COLUMN sector;

ALTER TABLE delsol_rqr
   ADD COLUMN sector character varying;

UPDATE delsol_rqr 
SET sector = delsol_delivery.sector
FROM delsol_delivery
WHERE delsol_rqr.delivery_id = delsol_delivery.id

ALTER TABLE delsol_rqr
   ALTER COLUMN sector SET NOT NULL;

select * from delsol_rqr where sector is null

delete from delsol_rqr where sector is null


   