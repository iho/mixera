async def create_tables(pool):
    async with pool.acquire() as conn:
        cur = await conn.cursor()
        await cur.execute('''CREATE TABLE IF NOT EXISTS users (
                                            id serial PRIMARY KEY,
                                            name TEXT UNIQUE NOT NULL,
                                            avatar TEXT NOT NULL,
                                            password TEXT NOT NULL
                                            )''')
        await cur.execute('''CREATE TABLE IF NOT EXISTS messagess (
                                            message_id serial PRIMARY KEY,
                                            user_id int references users(id),
                                            to_user int references users(id),
                                            message TEXT NOT NULL,

                                            time timestamp without time zone default (now() at time zone 'utc')

                                            )''')

async def create_user(pool, data):
    async with pool.acquire() as conn:
        cur = await conn.cursor()
        query = \
            '''
                INSERT INTO users 
                    (name, avatar, password) 
                VALUES 
                    (%(name)s, %(avatar)s, crypt(%(password)s, gen_salt('bf', 8))) 
                RETURNING id;
                '''
        await cur.execute(query, data)
        dict_id = await cur.fetchone()
        return dict_id

async def get_users(pool):
    async with pool.acquire() as conn:
        cur = await conn.cursor()
        query = \
            '''
                select 
                     id , name, avatar
                from users 
                '''
        await cur.execute(query)
        users = await cur.fetchall()
        return users


async def check_password(pool, data):
    async with pool.acquire() as conn:
        cur = await conn.cursor()
        query = \
            '''
                select * 
                from users 
                where 
                   name = %(name)s
                   and
                   password is NOT NULL 
                   and
                   password = crypt(%(password)s, password)
                   limit 1;
                '''
        await cur.execute(query, data)
        user = await cur.fetchone()
        return user

async def create_message(pool, data_old, user_id):
    data = data_old.copy()
    data['user_id'] = user_id
    data['to_user'] = data.get('to_user', None) 
    async with pool.acquire() as conn:
        cur = await conn.cursor()
        query = \
            '''
                INSERT INTO messagess
                    (user_id, to_user, message, time)
                VALUES 
                    (%(user_id)s, %(to_user)s,  %(message)s,  to_timestamp(%(time)s) AT TIME ZONE 'UTC')
                    RETURNING message_id;
    '''
        await cur.execute(query, data)

        message = await cur.fetchone()
        print(message)
        return message
