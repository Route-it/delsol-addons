select * from delsol_vehicle_model
where description like '%TRA%' and vehicle_type = 'auto'

select * from delsol_vehicle_model
where description like '%4000%' and vehicle_type = 'auto'

select * from delsol_vehicle_model
where description like '%C-%'

select * from delsol_vehicle_model
where description like '%CARG%' and vehicle_type = 'auto'

select distinct description from delsol_vehicle_model
where  vehicle_type = 'auto'



update delsol_vehicle_model
set vehicle_type = 'camion'
where description like '%CARG%' and vehicle_type = 'auto'

update delsol_vehicle_model
set vehicle_type = 'camion'
where description like '%C-%'

update delsol_vehicle_model
set vehicle_type = 'camion'
where description like '%4000%'


update delsol_vehicle_model
set vehicle_type = 'camion'
where description like '%TRAN%'
