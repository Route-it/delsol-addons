select * 
from delsol_delivery,delsol_vehicle
where delsol_delivery.vehicle_id = delsol_vehicle.id

update delsol_vehicle
set client_id = delsol_delivery.client_id
from delsol_delivery
where delsol_delivery.vehicle_id = delsol_vehicle.id


*************** De aca en adelante, ya se ejecuto en produccion. ********** 

-- actualizacion de colores de vehiculos no cargados.
update delsol_vehicle
set color = 1
where color is null

ALTER TABLE delsol_vehicle ALTER COLUMN color SET NOT NULL

verificar que no haya chasis repetidos: 
select nro_chasis from (select nro_chasis,count(*) as co from delsol_vehicle group by nro_chasis) a
where co >1

ALTER TABLE "delsol_vehicle" ADD CONSTRAINT "delsol_vehicle_vehicle_chasis_unique" unique(nro_chasis)


