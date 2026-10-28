import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path(__file__).with_name("library_data.json")


class Library:
    def __init__(self):
        self.books = []
        self.members = []
        self.loans = []
        self.load_data()

    def load_data(self):
        if not DATA_FILE.exists():
            return

        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            self.books = data.get("books", [])
            self.members = data.get("members", [])
            self.loans = data.get("loans", [])
        except (OSError, json.JSONDecodeError):
            print("Warning: Could not read data file.")

    def save_data(self):
        data = {
            "books": self.books,
            "members": self.members,
            "loans": self.loans
        }

        try:
            DATA_FILE.write_text(
                json.dumps(data, indent=2),
                encoding="utf-8"
            )
        except OSError as error:
            print(f"Error saving data: {error}")

    @staticmethod
    def next_id(items):
        return max((item["id"] for item in items), default=0) + 1

    @staticmethod
    def read_int(prompt, minimum=1):
        while True:
            try:
                number = int(input(prompt))

                if number < minimum:
                    print(f"Number must be at least {minimum}.")
                    continue

                return number

            except ValueError:
                print("Please enter a valid whole number.")

    def find_book(self, book_id):
        return next(
            (book for book in self.books if book["id"] == book_id),
            None
        )

    def find_member(self, member_id):
        return next(
            (member for member in self.members
             if member["id"] == member_id),
            None
        )

    # Book Management

    def add_book(self):
        print("\n--- Add Book ---")

        title = input("Book title: ").strip()
        author = input("Author: ").strip()

        if not title or not author:
            print("Title and author cannot be empty.")
            return

        copies = self.read_int("Number of copies: ")

        book = {
            "id": self.next_id(self.books),
            "title": title,
            "author": author,
            "total_copies": copies,
            "available_copies": copies
        }

        self.books.append(book)
        self.save_data()

        print(f"Book added successfully. Book ID: {book['id']}")

    def list_books(self):
        print("\n--- Book List ---")

        if not self.books:
            print("No books found.")
            return

        for book in self.books:
            print("-" * 35)
            print(f"ID: {book['id']}")
            print(f"Title: {book['title']}")
            print(f"Author: {book['author']}")
            print(f"Total copies: {book['total_copies']}")
            print(f"Available copies: {book['available_copies']}")

    def search_books(self):
        query = input("Search by title or author: ").strip().casefold()

        if not query:
            print("Search text cannot be empty.")
            return

        results = [
            book for book in self.books
            if query in book["title"].casefold()
            or query in book["author"].casefold()
        ]

        if not results:
            print("No books found.")
            return

        for book in results:
            print(
                f"ID: {book['id']} | "
                f"Title: {book['title']} | "
                f"Author: {book['author']} | "
                f"Available: {book['available_copies']}"
            )

    def edit_book(self):
        book_id = self.read_int("Book ID to edit: ")
        book = self.find_book(book_id)

        if book is None:
            print("Book not found.")
            return

        title = input(
            f"New title (leave empty to keep {book['title']}): "
        ).strip()

        author = input(
            f"New author (leave empty to keep {book['author']}): "
        ).strip()

        if title:
            book["title"] = title

        if author:
            book["author"] = author

        borrowed = book["total_copies"] - book["available_copies"]

        raw = input(
            f"Total copies (currently {book['total_copies']}, "
            "leave empty to keep): "
        ).strip()

        if raw:
            try:
                total = int(raw)

                if total < 1 or total < borrowed:
                    print("Invalid number of copies.")
                    return

                book["total_copies"] = total
                book["available_copies"] = total - borrowed

            except ValueError:
                print("Please enter a valid whole number.")
                return

        self.save_data()
        print("Book updated successfully.")

    def delete_book(self):
        book_id = self.read_int("Book ID to delete: ")
        book = self.find_book(book_id)

        if book is None:
            print("Book not found.")
            return

        if book["available_copies"] != book["total_copies"]:
            print("Cannot delete a book with active loans.")
            return

        confirm = input(
            f"Delete '{book['title']}'? (yes/no): "
        ).strip().lower()

        if confirm == "yes":
            self.books.remove(book)
            self.save_data()
            print("Book deleted.")
        else:
            print("Operation cancelled.")

    # Member Management

    def add_member(self):
        print("\n--- Add Member ---")

        name = input("Member full name: ").strip()

        if not name:
            print("Member name cannot be empty.")
            return

        member = {
            "id": self.next_id(self.members),
            "name": name
        }

        self.members.append(member)
        self.save_data()

        print(f"Member added. Member ID: {member['id']}")

    def list_members(self):
        print("\n--- Member List ---")

        if not self.members:
            print("No members found.")
            return

        for member in self.members:
            active_loans = sum(
                1 for loan in self.loans
                if loan["member_id"] == member["id"]
                and loan["return_date"] is None
            )

            print(
                f"ID: {member['id']} | "
                f"Name: {member['name']} | "
                f"Active loans: {active_loans}"
            )

    # Loan Management

    def borrow_book(self):
        if not self.books:
            print("Please add a book first.")
            return

        if not self.members:
            print("Please add a member first.")
            return

        self.list_books()
        book_id = self.read_int("Book ID: ")
        book = self.find_book(book_id)

        if book is None:
            print("Book not found.")
            return

        if book["available_copies"] < 1:
            print("No copies are available.")
            return

        self.list_members()
        member_id = self.read_int("Member ID: ")
        member = self.find_member(member_id)

        if member is None:
            print("Member not found.")
            return

        loan = {
            "id": self.next_id(self.loans),
            "book_id": book_id,
            "member_id": member_id,
            "borrow_date": datetime.now().isoformat(
                timespec="seconds"
            ),
            "return_date": None
        }

        self.loans.append(loan)
        book["available_copies"] -= 1

        self.save_data()

        print(
            f"'{book['title']}' borrowed by {member['name']}. "
            f"Loan ID: {loan['id']}"
        )

    def return_book(self):
        active_loans = [
            loan for loan in self.loans
            if loan["return_date"] is None
        ]

        if not active_loans:
            print("No active loans.")
            return

        self.list_loans(active_only=True)

        loan_id = self.read_int("Loan ID to return: ")

        loan = next(
            (
                item for item in active_loans
                if item["id"] == loan_id
            ),
            None
        )

        if loan is None:
            print("Active loan not found.")
            return

        book = self.find_book(loan["book_id"])

        if book is None:
            print("Book information not found.")
            return

        loan["return_date"] = datetime.now().isoformat(
            timespec="seconds"
        )

        book["available_copies"] += 1

        self.save_data()

        print(f"'{book['title']}' returned successfully.")

    def list_loans(self, active_only=False, member_id=None):
        loans = self.loans

        if active_only:
            loans = [
                loan for loan in loans
                if loan["return_date"] is None
            ]

        if member_id is not None:
            loans = [
                loan for loan in loans
                if loan["member_id"] == member_id
            ]

        if not loans:
            print("No loans found.")
            return

        print("\n--- Loan List ---")

        for loan in loans:
            book = self.find_book(loan["book_id"])
            member = self.find_member(loan["member_id"])

            title = book["title"] if book else "Unknown book"
            name = member["name"] if member else "Unknown member"

            status = (
                "Active"
                if loan["return_date"] is None
                else "Returned"
            )

            print("-" * 35)
            print(f"Loan ID: {loan['id']}")
            print(f"Book: {title}")
            print(f"Member: {name}")
            print(f"Borrow date: {loan['borrow_date']}")
            print(f"Status: {status}")

            if loan["return_date"] is not None:
                print(f"Return date: {loan['return_date']}")

    def member_loans(self):
        self.list_members()

        member_id = self.read_int("Member ID: ")

        if self.find_member(member_id) is None:
            print("Member not found.")
            return

        self.list_loans(member_id=member_id)


# Main Menu

def show_menu():
    print("""
========== Library Management ==========
1. Add book
2. Show books
3. Search books
4. Edit book
5. Delete book
6. Add member
7. Show members
8. Borrow book
9. Return book
10. Show all loans
11. Show active loans
12. Show member loans
0. Exit
========================================
""")


def main():
    library = Library()

    print("Library Management System Started!")

    actions = {
        "1": library.add_book,
        "2": library.list_books,
        "3": library.search_books,
        "4": library.edit_book,
        "5": library.delete_book,
        "6": library.add_member,
        "7": library.list_members,
        "8": library.borrow_book,
        "9": library.return_book,
        "10": library.list_loans,
        "11": lambda: library.list_loans(active_only=True),
        "12": library.member_loans
    }

    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        if choice == "0":
            library.save_data()
            print("Data saved. Goodbye!")
            break

        action = actions.get(choice)

        if action is None:
            print("Invalid option. Please choose a number from the menu.")
            continue

        try:
            action()
        except (EOFError, KeyboardInterrupt):
            print("\nProgram stopped.")
            library.save_data()
            break
        except Exception as error:
            print(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()
        