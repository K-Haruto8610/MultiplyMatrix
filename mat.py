#####################################################################
# 16*16の正方行列
# 参考：https://gitlab.com/iwatepu-sato-lab/idein/slam/py-videocore6/vc6-examples/-/blob/develop/basic_operations/fadd.py
#####################################################################
#coding:utf-8
import numpy as np

from videocore6.assembler import qpu
from videocore6.driver import Driver

@qpu
def kernel(asm):
    g = globals()
    g['reg_In_base']    = g['rf0']
    g['reg_In_stride']  = g['rf1']
    g['reg_Out_base']   = g['rf2']
    g['reg_Out_stride'] = g['rf3']

    g['reg_In_cur']     = g['rf4']
    g['reg_Out_cur']    = g['rf5']

    # uniformから値を取り出す
    # uniformの読み取り位置はインクリメントされる(pop的動作)
    nop(sig=ldunifrf(reg_In_base))
    nop(sig=ldunifrf(reg_In_stride))
    nop(sig=ldunifrf(reg_Out_base))
    nop(sig=ldunifrf(reg_Out_stride))
    nop(sig=ldunifrf(r3))

    eidx(r0)        # r0 = [0 ... 15]
    shl(r0, r0, 2)  # 各数値を4倍(float32のバイト数分)
    add(reg_In_cur,  reg_In_base,  r0) # Baseアドレスから ストライド=4バイトのアドレスベクトルを生成
    add(reg_Out_cur, reg_Out_base, r0) # Baseアドレスから ストライド=4バイトのアドレスベクトルを生成
    add(r3, r3, r0)
    # 合計値キャッシュの初期化
    mov(r1, 0)

    # データの読み込み
    # 配列Bの1列目を読み込む
    mov(tmua, r3, sig = thrsw)
    nop()
    nop()
    nop(sig = ldtmu(r2))
    for i in range(16):
      # データの読み込み
      # 配列Aを読み込む
      mov(tmua, reg_In_cur, sig = thrsw)
      nop()
      nop()
      nop(sig = ldtmu(r0))

      ### 計算処理を書くならここに書く ###
      fmul(r1, r2, r0)
      mov(tmud, r1)           # 書き出すデータ
      mov(tmua, reg_Out_cur)  # 書き出し先アドレスベクトル
      # addressのインクリメント
      add(reg_In_cur,  reg_In_cur,  reg_In_stride)
      add(reg_Out_cur, reg_Out_cur, reg_Out_stride)
    
    
    # GPUコードを終了する
    # 以下，なんかよくわからないがTMUを使った場合付けないと危ないのでつける
    nop(sig=thrsw)
    nop(sig=thrsw)
    nop()
    nop()
    nop(sig=thrsw)
    nop()
    nop()
    nop()


def main():
    with Driver() as drv:
        # Input vectors
        A_ref = np.full(16, 1).astype(dtype='float32')
        B_ref = np.full(16, 2).astype(dtype='float32')
        C_ref = np.full(16, 3).astype(dtype='float32')
        D_ref = np.full(16, 4).astype(dtype='float32')
        E_ref = np.full(16, 5).astype(dtype='float32')
        F_ref = np.full(16, 6).astype(dtype='float32')
        G_ref = np.full(16, 7).astype(dtype='float32')
        H_ref = np.full(16, 8).astype(dtype='float32')
        I_ref = np.full(16, 9).astype(dtype='float32')
        J_ref = np.full(16, 10).astype(dtype='float32')
        K_ref = np.full(16, 11).astype(dtype='float32')
        L_ref = np.full(16, 12).astype(dtype='float32')
        M_ref = np.full(16, 13).astype(dtype='float32')
        N_ref = np.full(16, 14).astype(dtype='float32')
        O_ref = np.full(16, 15).astype(dtype='float32')
        P_ref = np.full(16, 16).astype(dtype='float32')
        # A_ref = np.random.random(16).astype('float32')
        # B_ref = np.random.random(16).astype('float32')

        Ans = np.zeros((16, 16))

        # params setting
        inp = drv.alloc((16, 16), dtype='float32')
        out = drv.alloc((16, 16), dtype='float32')
        inp_T = drv.alloc((16, 16), dtype='float32')

        inp[0][:] = A_ref
        inp[1][:] = B_ref
        inp[2][:] = C_ref
        inp[3][:] = D_ref
        inp[4][:] = E_ref
        inp[5][:] = F_ref
        inp[6][:] = G_ref
        inp[7][:] = H_ref
        inp[8][:] = I_ref
        inp[9][:] = J_ref
        inp[10][:] = K_ref
        inp[11][:] = L_ref
        inp[12][:] = M_ref
        inp[13][:] = N_ref
        inp[14][:] = O_ref
        inp[15][:] = P_ref

        T_ref = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
        for i in range(16):
            inp_T[i][:] = T_ref
        
        out[0][:] = 0
        out[1][:] = 0
        out[2][:] = 0
        out[3][:] = 0
        out[4][:] = 0
        out[5][:] = 0
        out[6][:] = 0
        out[7][:] = 0
        out[8][:] = 0
        out[9][:] = 0
        out[10][:] = 0
        out[11][:] = 0
        out[12][:] = 0
        out[13][:] = 0
        out[14][:] = 0
        out[15][:] = 0

        # uniform setting
        unif = drv.alloc(5, dtype='uint32')
        unif[0] = inp.addresses()[0,0]
        unif[1] = inp.strides[0]
        unif[2] = out.addresses()[0,0]
        unif[3] = out.strides[0]
        unif[4] = inp_T.addresses()[0,0]

        # Run the program
        code = drv.program(kernel)
        drv.execute(code, unif.addresses()[0], thread=1)
        for i in range(16):
            for j in range(16):
                for k in range(16):
                    #drv.execute(code, unif.addresses()[0], thread=1)
                    Ans[j][i] = Ans[j][i] + out[j][k]

        print(Ans)
        print('')
        err = np.dot(inp, inp) - Ans
        print(err)       
if __name__ == '__main__':
    main()