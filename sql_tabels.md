# Order 

|Attribute|Datatype|Constraint|
|-|-|-|
|order_id|int|PRIMARY KEY|
|placed|DateTime||
|handled_by|VarChar(256)|NOT NULL|
|status|int|NOT NULL|
|handled_by|VarChar(256)|NOT NULL|


# Items

|Attribute|Datatype|Constraint|
|-|-|-|
|id|int|PRIMARY KEY|
|product|int|FOREIGN KEY Product.id|
|diet|VarChar(256)||
|belongs_to|int|FOREIGN KEY Order.order_id|


# Product

|Attribute|Datatype|Constraint|
|-|-|-|
|id|int|PRIMARY KEY|
|name|VarChar(256)|NOT NULL|
|cost|float|NOT NULL|
|avaliable|Bool|NOT NULL|
