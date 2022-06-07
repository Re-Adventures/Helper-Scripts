use std::io::Read;
use std::process;
use std::fs;
use std::env;

fn color_code_hex(elem: u8) -> String{
  return match elem{
    0         => format!("\x1b[31m{:02x}\x1b[0m", elem),
    1..=32    => format!("\x1b[33m{:02x}\x1b[0m", elem),
    48..=57   => format!("\x1b[35m{:02x}\x1b[0m", elem),
    127..=255 => format!("\x1b[34m{:02x}\x1b[0m", elem),
    _         => format!("\x1b[32m{:02x}\x1b[0m", elem),
  };
}

fn color_code_char(elem: u8) -> String{
  return match elem{
    0         => "\x1b[31m⋄\x1b[0m".to_string(),
    1..=32    => "\x1b[33m×\x1b[0m".to_string(),
    48..=57   => format!("\x1b[35m{}\x1b[0m", char::from(elem)),
    127..=255 => "\x1b[34m•\x1b[0m".to_string(),
    _         => format!("\x1b[32m{}\x1b[0m", char::from(elem)),
  };
}

fn read_file(filename: String) -> Vec<u8>{
  let mut tmp: Vec<u8> = Vec::new();
  let mut fp = fs::File::open(filename).expect("Failed in opening file");
  fp.read_to_end(&mut tmp).expect("Failed while reading file contents");
  return tmp;
}

fn main(){
  let argv: Vec<String> = env::args().collect();
  if argv.len() < 2{
    println!("Usage hexx <filename>");
    process::exit(1);
  }
  let data: Vec<u8> = read_file(argv[1].to_string());

  println!("┌────────┬─────────────────────────┬─────────────────────────┬────────┬────────┐");
  
  let mut i = 0;
  while i < data.len(){
    print!("│\x1b[36m{:08x}\x1b[0m│", i);

    for j in 0..16{
      if i + j >= data.len(){
        print!("   ");
      }
      else{
        print!(" {}", color_code_hex(data[i + j]));
      }
      if 7 == j{
        print!(" ┆");
      }
    }
    print!(" │");
    
    for j in 0..16{
      if (i + j) >= data.len(){
        print!(" ");
      }
      else{
        print!("{}", color_code_char(data[i + j]));
      }
      if 7 == j{
        print!("┆");
      }
    }
    println!("│");
    i += 16;
  }
  println!("└────────┴─────────────────────────┴─────────────────────────┴────────┴────────┘");

}
