declare @idColumn INT;
declare @idGender INT;

select @idColumn = min( id ) from gbo.category;

while @idColumn is not null
begin
    /*
        Do all the stuff that you need to do
    */
    select @idGender = genderId from gbo.category WHERE id=@idColumn
    INSERT INTO `beachhandball_2021`.`bh_tourn_category` (`created_at`, `name`, `abbreviation`, `classification`, `category`, `gbo_category_id`) 
VALUES (UNIX_TIMESTAMP(),(SELECT `name` FROM setup.gender WHERE id=@idGender), '', (SELECT `name` from gbo.category WHERE id=@idColumn), (SELECT `name` FROM setup.gender WHERE id=@idGender), @idColumn);

    select @idColumn = min( id ) from gbo.category where id > @idColumn
END;




FOR EACH ROW cat_row in gbo.category
BEGIN
   
END;


