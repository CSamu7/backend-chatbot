
all_terror = supabase.table("libros").select("id, titulo, num_paginas").ilike("gen", "%terror%").execute()
print(f"Total terror books: {len(all_terror.data) if all_terror.data else 0}")

# Try filtering with number
try:
    filtered_300 = supabase.table("libros").select("id, titulo, num_paginas").ilike("gen", "%terror%").lte("num_paginas", 300).execute()
    print(f"Terror books <= 300 pages (lte with int): {len(filtered_300.data) if filtered_300.data else 0}")
    if filtered_300.data:
        for b in filtered_300.data[:3]:
            print(f"  - {b.get('titulo')}: {b.get('num_paginas')}")
except Exception as e:
    print(f"Error with lte(int): {e}")

# Try filtering with string
try:
    filtered_300_str = supabase.table("libros").select("id, titulo, num_paginas").ilike("gen", "%terror%").lte("num_paginas", "300").execute()
    print(f"Terror books <= 300 pages (lte with str '300'): {len(filtered_300_str.data) if filtered_300_str.data else 0}")
    if filtered_300_str.data:
        for b in filtered_300_str.data[:3]:
            print(f"  - {b.get('titulo')}: {b.get('num_paginas')}")
except Exception as e:
    print(f"Error with lte(str): {e}")

# Check the exact pages from first 5 terror books
print("\n=== Sample horror books pages ===")
if all_terror.data:
    for b in all_terror.data[:5]:
        titulo = b.get('titulo')
        paginas = b.get('num_paginas')
        try:
            paginas_int = int(paginas)
            status = "✓" if paginas_int <= 300 else "✗"
            print(f"{status} {titulo}: {paginas} (int: {paginas_int})")
        except:
            print(f"? {titulo}: {paginas} (cannot convert to int)")
