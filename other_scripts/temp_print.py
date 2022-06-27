

pos_list=["a1","a2","a3","a4","a6","a7","a8","a9","a10","a11","b1","b2","b3","b4","b5","b6","b7","b8","b9","b10","b11","c1","c2","c3","c4","c5","c6","c7","c8","c9","c11","d1","d2","d4","d5","d6","d7","d9","d10","d11","e1","e2","e3","e4","e5","e6","e8","e9","e10","e11","f1","f8","f11","g1","g8","g9","g10","g11","h1","h2","h7","h8","h11","i2","i5","i6","i7","i10","i11","j1","j4","j5","j6","j8","j9","j10","j11","k1","k2","k3","k4","k5","k6","k8","k9","k10","k11"]

f_cur = open("temp/depth_11.pg","r")

lines = f_cur.readlines()

for i in range(len(pos_list)):
  new_file_name = "temp_new/depth_11_" + str(i) + ".pg"

  f_next = open(new_file_name, "w")

  f_next.write("#blackinitials\n" + str(pos_list[i]) + "\n")

  for line in lines[1:]:
    f_next.write(line)
