select * from delsol_delivery
where answered_poll = 't'
and state not in ('delivered') 
and state not in ('dispatched')

update delsol_delivery
set state = 'delivered'
where answered_poll = 't'
and state not in ('delivered') 
and state not in ('dispatched')

select * from delsol_delivery
where tae_stamp is not null
and state not in ('delivered')

update delsol_delivery
set state = 'delivered'
where tae_stamp is not null
and state not in ('delivered')

select * from delsol_delivery
where state = 'delivered'
and client_arrival is null

update delsol_delivery
set client_arrival = client_date
where state = 'delivered'
and client_arrival is null


select * from delsol_delivery where state = 'delivered'

update delsol_vehicle
set state = 'delivered'
from delsol_delivery
where delsol_delivery.vehicle_id = delsol_vehicle.id
and delsol_delivery.state = 'delivered'

select * from delsol_delivery where state = 'dispatched'

update delsol_vehicle
set state = 'dispatched'
from delsol_delivery
where delsol_delivery.vehicle_id = delsol_vehicle.id
and delsol_delivery.state = 'dispatched'

select * from delsol_delivery
where tae_stamp is null 
and delsol_delivery.state = 'delivered'

update delsol_delivery
set tae_stamp = delivery_date
where tae_stamp is null 
and delsol_delivery.state = 'delivered'

