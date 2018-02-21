select v.id,v.state,v.nro_chasis,d.id,d.state from delsol_vehicle as v left join delsol_delivery as d on v.id = d.vehicle_id
where nro_chasis in (
select chasis from (select RIGHT(nro_chasis,8)as chasis,count (*) as cant from delsol_vehicle
group by 1
having count (*) >1) as t1)




select v.nro_chasis from delsol_vehicle as v inner join
(select RIGHT(nro_chasis,8)as chasis,count (*) as cant from delsol_vehicle
group by 1
having count (*) >1) as b on v.nro_chasis like b.chasis