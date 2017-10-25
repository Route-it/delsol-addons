<Instalar app>

SELECT *
  FROM delsol_vehicle_model
where description like '%CARGO%'
or description like '%argo%'

UPDATE delsol_vehicle_model
   SET vehicle_type='camion'
where description like '%CARGO%'

UPDATE delsol_vehicle_model
   SET vehicle_type='camion'
where description like '%argo%'


update delsol_delivery
set sector = 'camiones'
from delsol_vehicle,delsol_vehicle_model
where delsol_delivery.vehicle_id = delsol_vehicle.id
and delsol_vehicle.modelo = delsol_vehicle_model.id
and vehicle_type like '%cam%'

update delsol_delivery
set sector = 'camiones'
where name like '%CARGO%'

update delsol_delivery
set sector = 'camiones'
where name like '%argo%'



