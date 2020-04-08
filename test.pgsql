select * from pe_pb;
select * from indice;
delete from pe_pb;
delete from indice;
commit;

select stockid from indice;