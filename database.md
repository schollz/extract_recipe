
Create a virtual table

```
create virtual table data using fts4(ndb_no,fdgrp_cd,long_desc,shrt_desc,comname,manufacname,sciname);
```

Populate it

```
insert into data(ndb_no,fdgrp_cd,long_desc,shrt_desc,comname,manufacname,sciname) select ndb_no,fdgrp_cd,long_desc,shrt_desc,comname,manufacname,sciname from food_des;
```

Select double word statements by ...

... selecting rows with words nearby
```
select * from data where data match 'olive NEAR oil';
```

... grabbing the beginning of the column

```
select * from data where shrt_desc match '^sweet potato' limit 4;
```
