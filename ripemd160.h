/* Clean RIPEMD-160 for fixed 32-byte input (SHA256 digest). Public-domain style. */
#ifndef RIPEMD160_H
#define RIPEMD160_H

#include <stdint.h>
#include <string.h>

static inline uint32_t _rol(uint32_t x, int n) {
    return (x << n) | (x >> (32 - n));
}

static void ripemd160_32(const uint8_t in[32], uint8_t out[20]) {
    uint32_t h0 = 0x67452301u, h1 = 0xEFCDAB89u, h2 = 0x98BADCFEu,
             h3 = 0x10325476u, h4 = 0xC3D2E1F0u;

    uint8_t block[64];
    memset(block, 0, 64);
    memcpy(block, in, 32);
    block[32] = 0x80;
    /* message bit-length = 256, little-endian */
    block[56] = 0x00;
    block[57] = 0x01;

    uint32_t X[16];
    for (int i = 0; i < 16; i++) {
        X[i] = (uint32_t)block[4 * i] |
               ((uint32_t)block[4 * i + 1] << 8) |
               ((uint32_t)block[4 * i + 2] << 16) |
               ((uint32_t)block[4 * i + 3] << 24);
    }

    static const uint32_t KL[5] = {0x00000000u, 0x5A827999u, 0x6ED9EBA1u, 0x8F1BBCDCu, 0xA953FD4Eu};
    static const uint32_t KR[5] = {0x50A28BE6u, 0x5C4DD124u, 0x6D703EF3u, 0x7A6D76E9u, 0x00000000u};
    static const int sl[80] = {
        11,14,15,12,5,8,7,9,11,13,14,15,6,7,9,8,
        7,6,8,13,11,9,7,15,7,12,15,9,11,7,13,12,
        11,13,6,7,14,9,13,15,14,8,13,6,5,12,7,5,
        11,12,14,15,14,15,9,8,9,14,5,6,8,6,5,12,
        9,15,5,11,6,8,13,12,5,12,13,14,11,8,5,6
    };
    static const int sr[80] = {
        8,9,9,11,13,15,15,5,7,7,8,11,14,14,12,6,
        9,13,15,7,12,8,9,11,7,7,12,7,6,15,13,11,
        9,7,15,11,8,6,6,14,12,13,5,14,13,13,7,5,
        15,5,8,11,14,14,6,14,6,9,12,9,12,5,15,8,
        8,5,12,9,12,5,14,6,8,13,6,5,15,13,11,11
    };
    static const int rl[80] = {
        0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,
        7,4,13,1,10,6,15,3,12,0,9,5,2,14,11,8,
        3,10,14,4,9,15,8,1,2,7,0,6,13,11,5,12,
        1,9,11,10,0,8,12,4,13,3,7,15,14,5,6,2,
        4,0,5,9,7,12,2,10,14,1,3,8,11,6,15,13
    };
    static const int rr[80] = {
        5,14,7,0,9,2,11,4,13,6,15,8,1,10,3,12,
        6,11,3,7,0,13,5,10,14,15,8,12,4,9,1,2,
        15,5,1,3,7,14,6,9,11,8,12,2,10,0,4,13,
        8,6,4,1,3,11,15,0,5,12,2,13,9,7,10,14,
        12,15,10,4,1,5,8,7,6,2,13,14,0,3,9,11
    };

    uint32_t al = h0, bl = h1, cl = h2, dl = h3, el = h4;
    uint32_t ar = h0, br = h1, cr = h2, dr = h3, er = h4;

    for (int i = 0; i < 80; i++) {
        uint32_t f;
        if (i < 16)      f = bl ^ cl ^ dl;
        else if (i < 32) f = (bl & cl) | (~bl & dl);
        else if (i < 48) f = (bl | ~cl) ^ dl;
        else if (i < 64) f = (bl & dl) | (cl & ~dl);
        else             f = bl ^ (cl | ~dl);
        uint32_t t = _rol(al + f + X[rl[i]] + KL[i / 16], sl[i]) + el;
        al = el; el = dl; dl = _rol(cl, 10); cl = bl; bl = t;

        if (i < 16)      f = br ^ (cr | ~dr);
        else if (i < 32) f = (br & dr) | (cr & ~dr);
        else if (i < 48) f = (br | ~cr) ^ dr;
        else if (i < 64) f = (br & cr) | (~br & dr);
        else             f = br ^ cr ^ dr;
        t = _rol(ar + f + X[rr[i]] + KR[i / 16], sr[i]) + er;
        ar = er; er = dr; dr = _rol(cr, 10); cr = br; br = t;
    }

    uint32_t t = h1 + cl + dr;
    h1 = h2 + dl + er;
    h2 = h3 + el + ar;
    h3 = h4 + al + br;
    h4 = h0 + bl + cr;
    h0 = t;

    out[0] = (uint8_t)h0; out[1] = (uint8_t)(h0 >> 8); out[2] = (uint8_t)(h0 >> 16); out[3] = (uint8_t)(h0 >> 24);
    out[4] = (uint8_t)h1; out[5] = (uint8_t)(h1 >> 8); out[6] = (uint8_t)(h1 >> 16); out[7] = (uint8_t)(h1 >> 24);
    out[8] = (uint8_t)h2; out[9] = (uint8_t)(h2 >> 8); out[10] = (uint8_t)(h2 >> 16); out[11] = (uint8_t)(h2 >> 24);
    out[12] = (uint8_t)h3; out[13] = (uint8_t)(h3 >> 8); out[14] = (uint8_t)(h3 >> 16); out[15] = (uint8_t)(h3 >> 24);
    out[16] = (uint8_t)h4; out[17] = (uint8_t)(h4 >> 8); out[18] = (uint8_t)(h4 >> 16); out[19] = (uint8_t)(h4 >> 24);
}

#endif
