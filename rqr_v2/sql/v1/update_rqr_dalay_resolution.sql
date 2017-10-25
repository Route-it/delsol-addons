select * from delsol_rqr


ALTER TABLE delsol_rqr
   ADD COLUMN delay_resolution_copy integer;

UPDATE delsol_rqr
   SET delay_resolution_copy=delay_resolution;

select create_date,delay_resolution,(create_date::date + delay_resolution::integer ) as fecha from delsol_rqr

select create_date,delay_resolution,(create_date + interval '1 day ' * delay_resolution::integer ) as fecha from delsol_rqr

<Instalar app>


update delsol_rqr
set progress_date = (create_date + interval '1 day ' * delay_resolution_copy::integer )
where state = 'solved'

update delsol_rqr
set solved_date = (create_date + interval '1 day ' * delay_resolution_copy::integer )
where state = 'solved'

update delsol_rqr
set solved_date = (create_date + interval '1 day ' * delay_resolution_copy::integer )
where state = 'closed'

update delsol_rqr
set closed_date = (create_date + interval '1 day ' * delay_resolution_copy::integer )
where state = 'closed'

select create_date,delay_resolution_copy,(create_date + interval '1 day ' * delay_resolution_copy::integer ) as progress_date
from delsol_rqr
where state = 'solved'


update delsol_rqr
set progress_date = (create_date + interval '1 day ' * delay_resolution_copy::integer )
where state = 'progress'
and progress_date is null

select * from delsol_rqr
where state = 'progress'
and progress_date is null

select * from delsol_rqr
where state = 'solved'
and solved_date is null

select * from delsol_rqr
where state = 'solved'
and progress_date is null

select * from delsol_rqr
where state = 'closed'
and progress_date is null

UPDATE delsol_rqr
   SET progress_date=solved_date
where state = 'closed'
and progress_date is null

select * from delsol_rqr
where state = 'closed'
and progress_date=solved_date

UPDATE delsol_rqr
   SET delay_to_take_action=delay_resolution
where state = 'closed'
and progress_date=solved_date



select * from delsol_rqr
where delay_to_take_action > delay_resolution
and state = 'solved'



select * from delsol_rqr
where state = 'closed'
and closed_date is null


UPDATE delsol_rqr
   SET delay_resolution=delay_resolution_copy;


select * from delsol_rqr
where delay_to_take_action = 345




ALTER TABLE delsol_rqr
   DROP COLUMN delay_resolution_copy;
