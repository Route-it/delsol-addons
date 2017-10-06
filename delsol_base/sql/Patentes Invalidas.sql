select d.name,v.patente,d.delivery_date as dd,d.state, v.nro_chasis as ch, count(*) from delsol_delivery as d, delsol_vehicle as v
where (char_length(v.patente) = 6
and (substring(v.patente from 1 for 1)<'O'
	or
     substring(v.patente from 1 for 1)>'P'))
and d.vehicle_id = v.id
group by ch,d.name,v.patente,d.delivery_date,d.state
union all
select d.name,v.patente,d.delivery_date,d.state, v.nro_chasis as ch, count(*) from delsol_delivery as d, delsol_vehicle as v     
 where (char_length(v.patente) = 7
and 
     substring(v.patente from 1 for 2)>'AB')
and d.vehicle_id = v.id
group by ch,d.name,v.patente,d.delivery_date,d.state
order by dd asc
