select * from delsol_rqr 
where delay_to_take_action > 30
and state not in ('closed','solved')

update delsol_rqr
set state = 'closed'
where delay_to_take_action > 30
and state not in ('closed','solved')



select * from delsol_rqr 
where delay_to_take_action > 30
and state in ('closed')
and closed_date is null


update delsol_rqr
set closed_date = '2017-10-23 00:00:00'
where delay_to_take_action > 30
and state in ('closed')
and closed_date is null



select * from delsol_rqr where id = 657