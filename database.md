
Create virtual tables and populate them

```
create virtual table data using fts4(ndb_no,fdgrp_cd,long_desc,shrt_desc,comname,manufacname,sciname);
insert into data(ndb_no,fdgrp_cd,long_desc,shrt_desc,comname,manufacname,sciname) select ndb_no,fdgrp_cd,long_desc,shrt_desc,comname,manufacname,sciname from food_des;

create virtual table nutrition_data using fts4(ndb_no,nutr_no,nutr_val);
insert into nutrition_data(ndb_no,nutr_no,nutr_val) select ndb_no,nutr_no,nutr_val from nut_data;

create virtual table nutrition_def using fts4(nutr_no,units,tagname);
insert into nutrition_def(nutr_no,units,tagname) select nutr_no,units,tagname from nutr_def;

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
